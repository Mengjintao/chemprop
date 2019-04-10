from argparse import Namespace
import csv
from logging import Logger
import os
from pprint import pformat
from typing import List, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from tensorboardX import SummaryWriter
import torch
from tqdm import trange
import pickle
from torch.optim.lr_scheduler import ExponentialLR
import GPy

from .evaluate import evaluate, evaluate_predictions
from .predict import predict
from .train import train
from chemprop.data import StandardScaler
from chemprop.data.utils import get_class_sizes, get_data, get_task_names, split_data
from chemprop.models import build_model
from chemprop.nn_utils import param_count
from chemprop.utils import build_optimizer, build_lr_scheduler, get_loss_func, get_metric_func, load_checkpoint,\
    makedirs, save_checkpoint


def morgan_fingerprint(smiles: str, radius: int = 3, num_bits: int = 2048, use_counts: bool = False) -> np.ndarray:
    """
    Generates a morgan fingerprint for a smiles string.

    :param smiles: A smiles string for a molecule.
    :param radius: The radius of the fingerprint.
    :param num_bits: The number of bits to use in the fingerprint.
    :param use_counts: Whether to use counts or just a bit vector for the fingerprint
    :return: A 1-D numpy array containing the morgan fingerprint.
    """
    if type(smiles) == str:
        mol = Chem.MolFromSmiles(smiles)
    else:
        mol = smiles
    if use_counts:
        fp_vect = AllChem.GetHashedMorganFingerprint(
            mol, radius, nBits=num_bits)
    else:
        fp_vect = AllChem.GetMorganFingerprintAsBitVect(
            mol, radius, nBits=num_bits)
    fp = np.zeros((1,))
    DataStructs.ConvertToNumpyArray(fp_vect, fp)

    return fp


def run_training(args: Namespace, logger: Logger = None) -> List[float]:
    """
    Trains a model and returns test scores on the model checkpoint with the highest validation score.

    :param args: Arguments.
    :param logger: Logger.
    :return: A list of ensemble scores for each task.
    """
    if logger is not None:
        debug, info = logger.debug, logger.info
    else:
        debug = info = print

    # Set GPU
    if args.gpu is not None:
        torch.cuda.set_device(args.gpu)

    # Print args
    debug(pformat(vars(args)))

    # Get data
    debug('Loading data')
    args.task_names = get_task_names(args.data_path)
    data = get_data(path=args.data_path, args=args, logger=logger)
    args.num_tasks = data.num_tasks()
    args.features_size = data.features_size()
    debug(f'Number of tasks = {args.num_tasks}')

    # Split data
    debug(f'Splitting data with seed {args.seed}')
    if args.separate_test_path:
        test_data = get_data(path=args.separate_test_path, args=args,
                             features_path=args.separate_test_features_path, logger=logger)
    if args.separate_val_path:
        val_data = get_data(path=args.separate_val_path, args=args,
                            features_path=args.separate_val_features_path, logger=logger)

    if args.separate_val_path and args.separate_test_path:
        train_data = data
    elif args.separate_val_path:
        train_data, _, test_data = split_data(data=data, split_type=args.split_type, sizes=(
            0.8, 0.2, 0.0), seed=args.seed, args=args, logger=logger)
    elif args.separate_test_path:
        train_data, val_data, _ = split_data(data=data, split_type=args.split_type, sizes=(
            0.8, 0.2, 0.0), seed=args.seed, args=args, logger=logger)
    else:
        train_data, val_data, test_data = split_data(
            data=data, split_type=args.split_type, sizes=args.split_sizes, seed=args.seed, args=args, logger=logger)

    if args.dataset_type == 'classification':
        class_sizes = get_class_sizes(data)
        debug('Class sizes')
        for i, task_class_sizes in enumerate(class_sizes):
            debug(f'{args.task_names[i]} '
                  f'{", ".join(f"{cls}: {size * 100:.2f}%" for cls, size in enumerate(task_class_sizes))}')

    if args.save_smiles_splits:
        with open(args.data_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)

            lines_by_smiles = {}
            indices_by_smiles = {}
            for i, line in enumerate(reader):
                smiles = line[0]
                lines_by_smiles[smiles] = line
                indices_by_smiles[smiles] = i

        all_split_indices = []
        for dataset, name in [(train_data, 'train'), (val_data, 'val'), (test_data, 'test')]:
            with open(os.path.join(args.save_dir, name + '_smiles.csv'), 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['smiles'])
                for smiles in dataset.smiles():
                    writer.writerow([smiles])
            with open(os.path.join(args.save_dir, name + '_full.csv'), 'w') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for smiles in dataset.smiles():
                    writer.writerow(lines_by_smiles[smiles])
            split_indices = []
            for smiles in dataset.smiles():
                split_indices.append(indices_by_smiles[smiles])
                split_indices = sorted(split_indices)
            all_split_indices.append(split_indices)
        with open(os.path.join(args.save_dir, 'split_indices.pckl'), 'wb') as f:
            pickle.dump(all_split_indices, f)

    if args.features_scaling:
        features_scaler = train_data.normalize_features(replace_nan_token=0)
        val_data.normalize_features(features_scaler)
        test_data.normalize_features(features_scaler)
    else:
        features_scaler = None

    args.train_data_size = len(train_data)

    debug(f'Total size = {len(data):,} | '
          f'train size = {len(train_data):,} | val size = {len(val_data):,} | test size = {len(test_data):,}')

    # Initialize scaler and scale training targets by subtracting mean and dividing standard deviation (regression only)
    if args.dataset_type == 'regression':
        debug('Fitting scaler')
        train_smiles, train_targets = train_data.smiles(), train_data.targets()
        scaler = StandardScaler().fit(train_targets)
        scaled_targets = scaler.transform(train_targets).tolist()
        train_data.set_targets(scaled_targets)
    else:
        scaler = None

    # Get loss and metric functions
    loss_func = get_loss_func(args)
    metric_func = get_metric_func(metric=args.metric)

    # Set up test set evaluation
    test_smiles, test_targets = test_data.smiles(), test_data.targets()
    sum_test_preds = np.zeros((len(test_smiles), args.num_tasks))
    all_test_preds = np.zeros(
        (len(test_smiles), args.num_tasks, args.ensemble_size))

    if args.confidence == "gaussian":
        sum_last_hidden = np.zeros(
            (len(val_data.smiles()), args.last_hidden_size))
        sum_last_hidden_test = np.zeros(
            (len(test_smiles), args.last_hidden_size))

    # Train ensemble of models
    for model_idx in range(args.ensemble_size):
        # Tensorboard writer
        save_dir = os.path.join(args.save_dir, f'model_{model_idx}')
        makedirs(save_dir)
        writer = SummaryWriter(log_dir=save_dir)

        # Load/build model
        if args.checkpoint_paths is not None:
            debug(
                f'Loading model {model_idx} from {args.checkpoint_paths[model_idx]}')
            model = load_checkpoint(
                args.checkpoint_paths[model_idx], current_args=args, logger=logger)
        else:
            debug(f'Building model {model_idx}')
            model = build_model(args)

        debug(model)
        debug(f'Number of parameters = {param_count(model):,}')
        if args.cuda:
            debug('Moving model to cuda')
            model = model.cuda()

        # Ensure that model is saved in correct location for evaluation if 0 epochs
        save_checkpoint(os.path.join(save_dir, 'model.pt'),
                        model, scaler, features_scaler, args)

        # Optimizers
        optimizer = build_optimizer(model, args)

        # Learning rate schedulers
        scheduler = build_lr_scheduler(optimizer, args)

        # Run training
        best_score = float('inf') if args.minimize_score else -float('inf')
        best_epoch, n_iter = 0, 0
        for epoch in trange(args.epochs):
            debug(f'Epoch {epoch}')

            n_iter = train(
                model=model,
                data=train_data,
                loss_func=loss_func,
                optimizer=optimizer,
                scheduler=scheduler,
                args=args,
                n_iter=n_iter,
                logger=logger,
                writer=writer
            )
            if isinstance(scheduler, ExponentialLR):
                scheduler.step()
            val_scores = evaluate(
                model=model,
                data=val_data,
                num_tasks=args.num_tasks,
                metric_func=metric_func,
                batch_size=args.batch_size,
                dataset_type=args.dataset_type,
                scaler=scaler,
                logger=logger
            )

            # Average validation score
            avg_val_score = np.nanmean(val_scores)
            debug(f'Validation {args.metric} = {avg_val_score:.6f}')
            writer.add_scalar(
                f'validation_{args.metric}', avg_val_score, n_iter)

            if args.show_individual_scores:
                # Individual validation scores
                for task_name, val_score in zip(args.task_names, val_scores):
                    debug(
                        f'Validation {task_name} {args.metric} = {val_score:.6f}')
                    writer.add_scalar(
                        f'validation_{task_name}_{args.metric}', val_score, n_iter)

            # Save model checkpoint if improved validation score
            if args.minimize_score and avg_val_score < best_score or \
                    not args.minimize_score and avg_val_score > best_score:
                best_score, best_epoch = avg_val_score, epoch
                save_checkpoint(os.path.join(save_dir, 'model.pt'),
                                model, scaler, features_scaler, args)

        # Evaluate on test set using model with best validation score
        info(
            f'Model {model_idx} best validation {args.metric} = {best_score:.6f} on epoch {best_epoch}')
        model = load_checkpoint(os.path.join(
            save_dir, 'model.pt'), cuda=args.cuda, logger=logger)

        test_preds = predict(
            model=model,
            data=test_data,
            batch_size=args.batch_size,
            scaler=scaler
        )
        test_scores = evaluate_predictions(
            preds=test_preds,
            targets=test_targets,
            num_tasks=args.num_tasks,
            metric_func=metric_func,
            dataset_type=args.dataset_type,
            logger=logger
        )

        if len(test_preds) != 0:
            sum_test_preds += np.array(test_preds)
            all_test_preds[:, :, model_idx] = np.array(test_preds)

        if args.confidence == "gaussian":
            model.eval()
            model.use_last_hidden = False
            last_hidden = predict(
                model=model,
                data=val_data,
                batch_size=args.batch_size,
                scaler=scaler
            )

            sum_last_hidden += np.array(last_hidden)

            last_hidden_test = predict(
                model=model,
                data=test_data,
                batch_size=args.batch_size,
                scaler=scaler
            )

            sum_last_hidden_test += np.array(last_hidden_test)

        # Average test score
        avg_test_score = np.nanmean(test_scores)
        info(f'Model {model_idx} test {args.metric} = {avg_test_score:.6f}')
        writer.add_scalar(f'test_{args.metric}', avg_test_score, 0)

        if args.show_individual_scores:
            # Individual test scores
            for task_name, test_score in zip(args.task_names, test_scores):
                info(
                    f'Model {model_idx} test {task_name} {args.metric} = {test_score:.6f}')
                writer.add_scalar(
                    f'test_{task_name}_{args.metric}', test_score, n_iter)

    # Evaluate ensemble on test set
    avg_test_preds = (sum_test_preds / args.ensemble_size)

    ensemble_scores = evaluate_predictions(
        preds=avg_test_preds.tolist(),
        targets=test_targets,
        num_tasks=args.num_tasks,
        metric_func=metric_func,
        dataset_type=args.dataset_type,
        logger=logger
    )
    # Average ensemble score
    avg_ensemble_test_score = np.nanmean(ensemble_scores)
    info(f'Ensemble test {args.metric} = {avg_ensemble_test_score:.6f}')
    writer.add_scalar(
        f'ensemble_test_{args.metric}', avg_ensemble_test_score, 0)

    if args.confidence and args.dataset_type == 'regression':
        if args.confidence == 'gaussian':
            kernel = GPy.kern.Linear(input_dim=args.last_hidden_size)

            avg_last_hidden = sum_last_hidden / args.ensemble_size
            avg_last_hidden_test = sum_last_hidden_test / args.ensemble_size

            transformed_val = scaler.transform(np.array(val_data.targets()))
            gaussian = GPy.models.GPRegression(
                avg_last_hidden, transformed_val, kernel)
            gaussian.optimize()

            avg_test_preds, avg_test_var = gaussian.predict(
                avg_last_hidden_test[:])

            # Scale Data
            domain = np.max(avg_test_var) - np.min(avg_test_var)
            # Shift.
            avg_test_var = avg_test_var - np.min(avg_test_var)
            # Scale domain to 1.
            avg_test_var = avg_test_var / domain
            # Apply log scale and flip.
            avg_test_var = np.maximum(0, -np.log(avg_test_var + np.exp(-10)))

            x = np.array([i[0] for i in avg_test_var])
            y = np.abs(np.array([scaler.inverse_transform(i[0])
                                 for i in avg_test_preds]) - np.array(test_targets))
        elif args.confidence == 'tanimoto':
            x = []
            y = []

            train_smiles_sfp = [morgan_fingerprint(s) for s in train_smiles]
            for i in range(len(test_smiles)):
                smiles = Chem.MolToSmiles(Chem.MolFromSmiles(test_smiles[i]))
                fp = morgan_fingerprint(smiles)
                morgan_sim = []
                for sfp in train_smiles_sfp:
                    tsim = np.dot(fp, sfp) / (fp.sum() +
                                              sfp.sum() - np.dot(fp, sfp))
                    morgan_sim.append(
                        (tsim, np.abs(avg_test_preds[i] - test_targets[i][0])))
                morgan_sim, error = max(morgan_sim, key=lambda x: x[0])
                x.append(morgan_sim)
                y.append(error)

            x = np.array(x) * 10
            y = np.array(y)

        elif args.confidence == 'ensemble':
            x, y = np.var(all_test_preds, axis=2) * -1, np.abs(avg_test_preds - test_targets)

        confidence_visualizations(args, x=x, y=y)

    if args.confidence and args.dataset_type == 'classification':
        kernel = GPy.kern.Linear(input_dim=args.last_hidden_size)

        avg_last_hidden = sum_last_hidden / args.ensemble_size
        avg_last_hidden_test = sum_last_hidden_test / args.ensemble_size

        gaussian = GPy.models.GPRegression(
            avg_last_hidden, np.array(val_data.targets()), kernel)
        gaussian.optimize()

        avg_test_preds, avg_test_var = gaussian.predict(
            avg_last_hidden_test[:])

        y = np.array([i[0] for i in avg_test_preds]) - \
            np.array([i[0] for i in test_targets[:]])
        y = np.abs(y)

        plt.plot(avg_test_var, y, 'ro')
        plt.show()

        # Scale Data
        domain = np.max(avg_test_var) - np.min(avg_test_var)
        # Shift.
        avg_test_var = avg_test_var - np.min(avg_test_var)
        # Scale domain to 1.
        avg_test_var = avg_test_var / domain
        # Apply log scale and flip.
        avg_test_var = np.maximum(0, -np.log(avg_test_var + np.exp(-10)))

        x = np.array([i[0] for i in avg_test_var])

        plt.plot(x, y, 'ro')
        plt.show()

    # Individual ensemble scores
    if args.show_individual_scores:
        for task_name, ensemble_score in zip(args.task_names, ensemble_scores):
            info(
                f'Ensemble test {task_name} {args.metric} = {ensemble_score:.6f}')

    return ensemble_scores


def confidence_visualizations(args: Namespace, x: List[Union[float, int]] = [], y: List[Union[float, int]] = []):
    pairs_by_confidence = sorted(list(zip(x, y)), key=lambda pair: pair[0])
    pairs_by_error = sorted(list(zip(x, y)), key=lambda pair: pair[1])

    metric_func = get_metric_func(metric=args.metric)

    if args.g_cutoff_discrete:
        for i in range(10):
            c = int((i/10) * len(pairs_by_confidence))
            kept = (len(pairs_by_confidence) - c) / len(pairs_by_confidence)
            print(f'Cutoff: {pairs_by_confidence[c][0]}',
                  f'{args.metric}: {metric_func([pair[0] for pair in pairs_by_confidence[c:]], [pair[1] for pair in pairs_by_confidence[c:]])}',
                  f'% Results Kept: {int(kept*100)}%')

        # Calculate Ideal Cutoffs
        for i in range(10):
            c = int((1 - i/10) * len(pairs_by_error))
            kept = c / len(pairs_by_error)
            print(f'{args.metric}: {metric_func([pair[0] for pair in pairs_by_error[:c]], [pair[1] for pair in pairs_by_error[:c]])}',
                  f'% Results Kept: {int(kept*100)}%')

    plt.plot(x, y, 'ro')

    if args.g_cutoff:
        cutoff = []
        rmse = []
        square_error = [pair[1]*pair[1] for pair in pairs_by_confidence]
        for i in range(len(pairs_by_confidence)):
            cutoff.append(pairs_by_confidence[i][0])
            rmse.append(np.sqrt(np.mean(square_error[i:])))

        print(cutoff, rmse)
        plt.plot(cutoff, rmse)

    if args.g_bootstrap:
        # Perform Bootstrapping at 95% confidence.
        sum_subset = sum([val[0]
                          for val in pairs_by_confidence[:args.bootstrap[0]]])

        x_confidence = []
        y_confidence = []

        for i in range(args.bootstrap[0], len(pairs_by_confidence)):
            x_confidence.append(sum_subset/args.bootstrap[0])

            ys = [val[1] for val in pairs_by_confidence[i-args.bootstrap[0]:i]]
            y_sum = 0
            for j in range(args.bootstrap[2]):
                y_sum += sorted(np.random.choice(ys,
                                                 args.bootstrap[1]))[-int(args.bootstrap[1]/20)]

            y_confidence.append(y_sum / args.bootstrap[2])
            sum_subset -= pairs_by_confidence[i-args.bootstrap[0]][0]
            sum_subset += pairs_by_confidence[i][0]

        plt.plot(x_confidence, y_confidence)

    plt.show()

    if args.g_histogram:
        scale = np.average(y) * 5

        for i in range(5):
            errors = []
            for pair in pairs_by_confidence:
                if pair[0] < 2 * i or pair[0] > 2 * (i + 1):
                    continue
                errors.append(pair[1])
            plt.hist(errors, bins=10, range=(0, scale))
            plt.show()

    if args.g_joined_histogram:
        bins = 8
        scale = np.average(y) * bins / 2

        errors_by_confidence = [[] for _ in range(10)]
        for pair in pairs_by_confidence:
            if pair[0] == 10:
                continue

            errors_by_confidence[int(pair[0])].append(pair[1])

        errors_by_bin = [[] for _ in range(bins)]
        for interval in errors_by_confidence:
            error_counts, _ = np.histogram(
                np.minimum(interval, scale), bins=bins)
            for i in range(bins):
                if len(interval) == 0:
                    errors_by_bin[i].append(0)
                else:
                    errors_by_bin[i].append(
                        error_counts[i] / len(interval) * 100)

        colors = ['green', 'yellow', 'orange', 'red',
                  'purple', 'blue', 'brown', 'black']
        sum_heights = [0 for _ in range(10)]
        for i in range(bins):
            label = f'Error of {i * scale / bins} to {(i + 1) * scale / bins}'

            if i == bins - 1:
                label = f'Error {i * scale / bins} +'
            plt.bar(list(
                range(10)), errors_by_bin[i], color=colors[i], bottom=sum_heights, label=label)
            sum_heights = [sum_heights[j] + errors_by_bin[i][j]
                           for j in range(10)]

        names = (
            f'{i} to {i+1} \n {len(errors_by_confidence[i])} points' for i in range(10))
        plt.xticks(list(range(10)), names)
        plt.xlabel("Confidence")
        plt.ylabel("Percent of Test Points")
        plt.legend()

        plt.show()

    if args.g_joined_boxplot:
        errors_by_confidence = [[] for _ in range(10)]
        for pair in pairs_by_confidence:
            if pair[0] == 10:
                continue

            errors_by_confidence[int(pair[0])].append(pair[1])

        fig, ax = plt.subplots()
        ax.set_title('Joined Boxplot')
        ax.boxplot(errors_by_confidence)

        names = (
            f'{i} to {i+1} \n {len(errors_by_confidence[i])} points' for i in range(10))
        plt.xticks(list(range(1, 11)), names)
        plt.xlabel("Confidence")
        plt.ylabel("Absolute Value of Error")
        plt.legend()
        plt.show()
