import numpy as np
import matplotlib.pyplot as plt
from copy import copy

def _norm_by_row(m):
    rows_shift_to_0 = (m - np.min(m, axis=1)[:, np.newaxis])
    rows_max_magnitude = np.ptp(m, axis=1)[:, np.newaxis]
    row_normalized_m = np.divide(rows_shift_to_0, rows_max_magnitude, 
                                out=np.zeros(m.shape), 
                                where=rows_max_magnitude!=0)
    return row_normalized_m

def plot_heatmat_mgs_offset(sar_by_svid_matrix, max_y_axis, y_ticks, y_label, title, log_norm=False):

    sar_by_svid_matrix = list(sar_by_svid_matrix)

    total_messages = np.zeros((max_y_axis, 30))
    for i in np.arange(max_y_axis):
        tows_mod_60_sec = [tow % 60 for tow in sar_by_svid_matrix[i]]
        unique_tows, counts = np.unique(tows_mod_60_sec, return_counts=True)
        for tow, count in zip(unique_tows, counts):
            total_messages[i][tow//2] = count

    row_normalized_total_messages = _norm_by_row(total_messages)

    log_cmap = copy(plt.get_cmap('viridis'))
    log_cmap.set_bad(log_cmap(0))

    plt.figure(figsize=(9,6))
    plt.title(title)
    if log_norm:
        plt.pcolormesh(row_normalized_total_messages, cmap=log_cmap, edgecolors='k', linewidths=0.5, norm='log')
    else:
        plt.pcolormesh(row_normalized_total_messages, cmap=log_cmap, edgecolors='k', linewidths=0.5)
    plt.yticks(np.arange(max_y_axis) + 0.5, y_ticks)
    plt.xticks(np.arange(30) + 0.5, [str(i) for i in np.arange(1,61,2)])
    plt.ylabel(y_label)
    plt.xlabel(f"Reception time of the last page of the SAR message (s)")
    plt.tight_layout()
    plt.colorbar()

