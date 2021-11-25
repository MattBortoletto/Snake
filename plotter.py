import matplotlib.pyplot as plt
from IPython import display

#plt.ion()

def live_plot_scores(scores, mean_scores=None):
  display.clear_output(wait=True)
  display.display(plt.gcf())
  plt.clf()
  plt.title("Real time training scores")
  plt.xlabel("Number of games")
  plt.ylabel("Score")
  plt.plot(scores, label="Single game score")
  if mean_scores is not None:
    plt.plot(moving_average(mean_scores), label="Moving average")
  plt.legend()
  plt.grid(ls="--")
  plt.ylim(ymin=0)
  plt.text(len(scores)-1, scores[-1], str(scores[-1]))
  plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
  plt.show(block=False)
  plt.pause(0.1)


def moving_average(x, n=20) :
  ret = np.cumsum(x, dtype=float)
  ret[n:] = ret[n:] - ret[:-n]
  return ret[n - 1:] / n
