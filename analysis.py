import pandas as pd
import numpy as np
from scipy import stats
import math
import matplotlib.pyplot as plt

assignment = pd.read_csv("data/ab_assignment.csv", parse_dates=["assignment_time"])
events = pd.read_csv("data/onboarding_events.csv", parse_dates=["event_time"])
post = pd.read_csv("data/post_metrics.csv")

ab = assignment.merge(post, on="user_id")

def prop_test(success_a, n_a, success_b, n_b):
    p_pool = (success_a + success_b) / (n_a + n_b)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    z = (success_b / n_b - success_a / n_a) / se
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    diff = success_b / n_b - success_a / n_a
    return diff, z, p

summary = ab.groupby("experiment_group").agg(
    users=("user_id", "count"),
    completion_rate=("account_completed", "mean"),
    retention_7d=("retention_7d", "mean"),
    complaint_7d=("complaint_7d", "mean"),
    first_deposit_7d=("first_deposit_7d", "mean")
).reset_index()
print(summary)

ctrl = ab[ab["experiment_group"] == "control"]
trt = ab[ab["experiment_group"] == "treatment"]

for metric in ["account_completed", "retention_7d", "complaint_7d"]:
    diff, z, p = prop_test(ctrl[metric].sum(), len(ctrl), trt[metric].sum(), len(trt))
    print(metric, diff, z, p)

funnel = (
    events[events["status"] == "success"]
    .merge(assignment[["user_id", "experiment_group"]], on="user_id")
    .groupby(["experiment_group", "step_no", "event_name"])["user_id"]
    .nunique()
    .reset_index(name="users")
    .sort_values(["experiment_group", "step_no"])
)
funnel["rate_from_start"] = funnel.groupby("experiment_group")["users"].transform(lambda s: s / s.iloc[0])
print(funnel)

channel_uplift = (
    assignment.merge(post, on="user_id")
    .groupby(["channel", "experiment_group"])["account_completed"]
    .mean()
    .unstack()
    .reset_index()
)
channel_uplift["uplift_ppt"] = (channel_uplift["treatment"] - channel_uplift["control"]) * 100
print(channel_uplift.sort_values("uplift_ppt", ascending=False))

plt.figure(figsize=(8, 5))
for grp in ["control", "treatment"]:
    tmp = funnel[funnel["experiment_group"] == grp]
    plt.plot(tmp["step_no"], tmp["rate_from_start"] * 100, marker="o", label=grp)
plt.ylabel("Users remaining from start (%)")
plt.title("Onboarding funnel")
plt.legend()
plt.tight_layout()
plt.savefig("figures/reproduce_onboarding_funnel.png", dpi=150)
