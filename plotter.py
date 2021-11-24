from IPython import display

plt.ion()

def plot_scores(scores, mean_scores):
  display.clear_output(wait=True)
  display.display(plt.gcf())
  plt.clf()
  plt.title("Real time training scores")
  plt.xlabel("Number of games")
  plt.ylabel("Score")
  plt.plot(scores, label="Single game score")
  plt.plot(mean_scores, label="Average score")
  plt.legend()
  plt.grid()
  plt.ylim(ymin=0)
  plt.text(len(scores)-1, scores[-1], str(scores[-1]))
  plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
