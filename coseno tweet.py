import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("./similitud_tweets_tf.csv")
feats = [c for c in df.columns if c not in ("documento", "tipo")]

semillas = df[df["tipo"] == "semilla"].set_index("documento")[feats]
tweets = df[df["tipo"] == "tweet"].set_index("documento")[feats]

sim_sem = pd.DataFrame(
    cosine_similarity(tweets.values, semillas.values),
    index=tweets.index, columns=semillas.index,
)
sim_tw = pd.DataFrame(
    cosine_similarity(tweets.values),
    index=tweets.index, columns=tweets.index,
)

print(sim_sem.round(3))
# TODO: imprime pares i<j con sim_tw >= 0.90