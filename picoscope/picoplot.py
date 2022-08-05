from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


class Picoplot:
    '''For testing to tune voltage gain. Don't use during experiments because it holds every waveform in memory.'''

    def __init__(self):
        plt.clf()
        self.fig, self.axs = plt.subplots(2)
        self.ax2 = self.axs[0].twinx()


    def freq_step(self, frequencies: np.array, dwell: float):
        """Frequency step plot.

        Args:
            frequencies (np.array): List of frequencies used in sweep.
            dwell (float): Duration of each frequency in sweep.
        """

        no_freqs = len(frequencies)
        freqs = np.insert(frequencies, 0, 0)
        t_freqs = np.linspace(0, no_freqs * dwell, no_freqs + 1)
        
        self.ax2.step(t_freqs, freqs/1000, where='pre', zorder=1, c='k')
        self.ax2.set_zorder(self.ax2.get_zorder() + 1)
        self.ax2.patch.set_visible(False)
        self.ax2.set_ylabel('f [kHz]')
        self.ax2.set_xlim(left=0)
        now = datetime.now()
        self.ax2.set_title(now.strftime("%Y-%m-%d %H:%M"))


    def plot_dft(self, freq_bins: np.array, amps: np.array):
        """A lineplot of discrete fourier transform.
        
        freq_bins (np.array): Frequency bins.
        amps (np.array): Frequency bin amplitudes.
        """

        self.axs[1].plot(freq_bins/1000, amps, c='k')
        self.axs[1].set_xlabel('Frequency [kHz]')
        self.axs[1].set_ylabel('Amplitude [a.u.]')
        self.axs[1].set_xlim(left=0, right=200)


    def plot_params(self, params: dict):
        """Plots params value on fig.
        
        Args:
            params (float): Picoscope params.
        """

        y_pos = 0.6
        for i, (key, val) in enumerate(params.items()):
            self.ax2.annotate(f'{key}: {val:.1e}',
                            xy=[1.14, y_pos-0.05*i],
                            xycoords='axes fraction',
                            color='k',
                            backgroundcolor='w',
                            fontsize=8,
                            annotation_clip=False)


    def plot_waveform(self, wave: list, duration: float):
        """Plots raw waveform.

        Args:
            wave (list): Yeaaaaaaa.
            duration (float): Sweep duration.
        """
        sweep_linspace = np.linspace(0, duration, len(wave))
        self.axs[0].plot(sweep_linspace,
                      wave,
                      c='g',
                      zorder=2,
                      linewidth=.5)

        self.axs[0].set_xlabel('t [s]')
        self.axs[0].set_ylabel('Amplitude [mV]')
        self.axs[0].set_xlim(left=0)


    def save(self):
        now = datetime.now()

        plt.savefig(
            f'tests/data/test_fig_{now.strftime("%Y-%m-%d %H:%M")}.png'
        )

        return 'figure saved'