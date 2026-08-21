import argparse
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


REQUIRED_COLUMNS = [
    'control_time',
    'information_age',
    'slave_id',
    'predecessor_position',
    'slave_position',
    'predecessor_velocity',
    'slave_velocity',
    'actual_distance',
    'desired_distance',
    'distance_error',
    'velocity_error',
    'acceleration'
]


def load_csv(path):
    data = pd.read_csv(path)

    missing = [
        column for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            f'{path} is missing columns: {missing}'
        )

    return data


def select_interval(data, start_time, end_time):
    return data[
        (data['control_time'] >= start_time) &
        (data['control_time'] <= end_time)
    ].copy()


def l2_norm(data, column):
    t = data['control_time'].to_numpy()
    x = data[column].to_numpy()

    if len(t) < 2:
        return float('nan')

    return np.sqrt(
        np.trapz(x ** 2, t)
    )


def rms(data, column):
    x = data[column].to_numpy()

    if len(x) == 0:
        return float('nan')

    return np.sqrt(
        np.mean(x ** 2)
    )


def max_abs(data, column):
    x = data[column].to_numpy()

    if len(x) == 0:
        return float('nan')

    return np.max(np.abs(x))


def save_plot(
    datasets,
    x_column,
    y_column,
    ylabel,
    title,
    filename,
    output_dir
):
    plt.figure(figsize=(9, 5))

    for label, data in datasets:
        plt.plot(
            data[x_column],
            data[y_column],
            label=label
        )

    plt.xlabel('Time (s)')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    path = os.path.join(
        output_dir,
        filename
    )

    plt.savefig(
        path,
        dpi=300,
        bbox_inches='tight'
    )

    plt.close()


def main():

    parser = argparse.ArgumentParser(
        description=(
            'Analyse three-follower vehicle platooning '
            'string-stability experiment.'
        )
    )

    parser.add_argument(
        '--slave1',
        required=True
    )

    parser.add_argument(
        '--slave2',
        required=True
    )

    parser.add_argument(
        '--slave3',
        required=True
    )

    parser.add_argument(
        '--label',
        default='String Stability Experiment'
    )

    parser.add_argument(
        '--start',
        type=float,
        default=10.0,
        help='Analysis start time in seconds'
    )

    parser.add_argument(
        '--end',
        type=float,
        default=30.0,
        help='Analysis end time in seconds'
    )

    parser.add_argument(
        '--output-dir',
        default='string_stability_results'
    )

    args = parser.parse_args()

    os.makedirs(
        args.output_dir,
        exist_ok=True
    )

    slave1 = load_csv(args.slave1)
    slave2 = load_csv(args.slave2)
    slave3 = load_csv(args.slave3)

    datasets = [
        ('Slave 1', slave1),
        ('Slave 2', slave2),
        ('Slave 3', slave3)
    ]

    analysis_data = []

    for label, data in datasets:

        interval = select_interval(
            data,
            args.start,
            args.end
        )

        analysis_data.append(
            (label, interval)
        )

    # -------------------------------------------------
    # Metrics
    # -------------------------------------------------

    results = []

    for label, data in analysis_data:

        results.append({
            'vehicle': label,
            'L2_spacing_error':
                l2_norm(data, 'distance_error'),

            'RMS_spacing_error':
                rms(data, 'distance_error'),

            'max_abs_spacing_error':
                max_abs(data, 'distance_error'),

            'RMS_velocity_error':
                rms(data, 'velocity_error'),

            'max_information_age':
                data['information_age'].max()
        })

    metrics = pd.DataFrame(results)

    e1 = metrics.loc[
        metrics['vehicle'] == 'Slave 1',
        'L2_spacing_error'
    ].iloc[0]

    e2 = metrics.loc[
        metrics['vehicle'] == 'Slave 2',
        'L2_spacing_error'
    ].iloc[0]

    e3 = metrics.loc[
        metrics['vehicle'] == 'Slave 3',
        'L2_spacing_error'
    ].iloc[0]

    g21 = e2 / e1
    g32 = e3 / e2

    print()
    print('==========================================')
    print(args.label)
    print(
        f'Analysis interval: '
        f'{args.start:.1f} - {args.end:.1f} s'
    )
    print('==========================================')
    print()

    print(
        metrics.to_string(
            index=False
        )
    )

    print()
    print(f'G21 = ||e2||2 / ||e1||2 = {g21:.4f}')
    print(f'G32 = ||e3||2 / ||e2||2 = {g32:.4f}')

    if g21 <= 1.0 and g32 <= 1.0:
        print(
            'Result: no L2 spacing-error amplification '
            'was observed along the vehicle string.'
        )
    else:
        print(
            'Result: L2 spacing-error amplification '
            'was observed in at least one link.'
        )

    metrics['G_to_predecessor'] = [
        np.nan,
        g21,
        g32
    ]

    metrics.to_csv(
        os.path.join(
            args.output_dir,
            'string_stability_metrics.csv'
        ),
        index=False
    )

    # -------------------------------------------------
    # Plots
    # -------------------------------------------------

    save_plot(
        datasets,
        'control_time',
        'distance_error',
        'Spacing Error (m)',
        f'{args.label} - Spacing Error',
        'spacing_error.png',
        args.output_dir
    )

    save_plot(
        datasets,
        'control_time',
        'slave_velocity',
        'Velocity (m/s)',
        f'{args.label} - Vehicle Velocities',
        'slave_velocities.png',
        args.output_dir
    )

    save_plot(
        datasets,
        'control_time',
        'actual_distance',
        'Inter-Vehicle Distance (m)',
        f'{args.label} - Actual Inter-Vehicle Distance',
        'actual_distance.png',
        args.output_dir
    )

    save_plot(
        datasets,
        'control_time',
        'information_age',
        'Information Age (s)',
        f'{args.label} - Communication Information Age',
        'information_age.png',
        args.output_dir
    )

    print()
    print(
        f'Results saved in: '
        f'{os.path.abspath(args.output_dir)}'
    )


if __name__ == '__main__':
    main()
