import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor, plot_tree, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt


# I - preparing the data
path_to_csv = "D:/dossier_y23hallo/Thèse/multi-energy/FINAL-RESULTS/SRL/FINAL"  # path to inference results folder

# 1. RL decisions dataframe
decisions_file = "Inference_RL_decisions"
df = pd.read_csv(path_to_csv + "/" + decisions_file + ".csv", sep=",")
df_1 = df.iloc[:5304]  # electric microgrid
df_1 = df_1.drop("Energy_Storage", axis=1)
df_1 = df_1.drop("aggregator", axis=1)
df_1.columns = ['C_elec', 'P_elec', 'mainGrid', 'PAC_elec', 'CHP_elec']
df_1 = df_1.drop("P_elec", axis=1)
df_1 = df_1.reset_index(drop=True)
df_2 = df.iloc[5304:]  # district heating network
df_2 = df_2.drop("Energy_Conversion_3", axis=1)
df_2 = df_2.drop("aggregator", axis=1)
df_2.columns = ['C_th', 'P_th', 'TES', 'PAC_th', 'CHP_th']
df_2 = df_2.drop("C_th", axis=1)
df_2 = df_2.reset_index(drop=True)
decision_df = pd.concat([df_1, df_2], axis=1)

# 2. states dataframe
states_file = "states"
feature_df = pd.read_csv(path_to_csv + "/" + states_file + ".csv", sep=",")
timeless_feature_df = feature_df.drop("t", axis=1)


# II - initializing the tree
# 3. Train/test split - with time & without time + shuffling
# X1_train, X1_test, y1_train, y1_test = train_test_split(
#     feature_df,
#     decision_df,
#     test_size=0.2,
#     random_state=42
# )  # with time feature
X2_train, X2_test, y2_train, y2_test = train_test_split(
    timeless_feature_df,
    decision_df,
    shuffle=True,
    test_size=0.2,
    random_state=42
)  # without time feature & with shuffling

# 4. creation of the classifiers
# tree_1 = DecisionTreeRegressor(
#     max_depth=3,
#     min_samples_leaf=200,
#     random_state=42
# )
tree_2 = DecisionTreeRegressor(
    max_depth=7,
    min_samples_leaf=200,
    random_state=42
)

# 5. training the decision trees
# tree_1.fit(X1_train, y1_train)
tree_2.fit(X2_train, y2_train)

# 6. prediction & quick evaluation & R2 scores
# y1_pred = tree_1.predict(X1_test)
# score = tree_1.score(X1_test, y1_test)
# print(f"Decision tree score with time feature -> {score}")
# r2_tree1 = r2_score(
#     y1_test,
#     y1_pred,
#     multioutput="uniform_average"
# )  # R² overall the decision
# print(f"Decision tree score with time feature R² score -> {r2_tree1}")
# r2_tree1_per_action = r2_score(
#     y1_test,
#     y1_pred,
#     multioutput="raw_values"
# )
# for action_name, score in zip(decision_df.columns, r2_tree1_per_action):  # per-action R² overall the decision
#     print(action_name, score)

y2_pred = tree_2.predict(X2_test)
score = tree_2.score(X2_test, y2_test)
print(f"Decision tree score without time feature and with shuffling -> {score}")
r2_tree2 = r2_score(
    y2_test,
    y2_pred,
    multioutput="uniform_average"
)  # R² overall the decision
print(f"Decision tree score without time feature and with shuffling R² score -> {r2_tree2}")
r2_tree2_per_action = r2_score(
    y2_test,
    y2_pred,
    multioutput="raw_values"
)
for action_name, score in zip(decision_df.columns, r2_tree2_per_action):  # per-action R² overall the decision
    print(action_name, score)

# 7. plotting the decision trees
plt.figure()
# plt.figure(figsize=(20,10))
# plot_tree(
#     tree_1,
#     feature_names=feature_df.columns,
#     filled=True,
#     rounded=True,
#     fontsize=8
# )
# # plt.tight_layout()
# plt.show()
# plt.savefig(path_to_csv + '/' + "Time_decision_tree.pdf", format="pdf", bbox_inches="tight")
# plt.close()
plot_tree(
    tree_2,
    feature_names=timeless_feature_df.columns,
    filled=True,
    rounded=True,
    fontsize=8
)
# plt.tight_layout()
plt.show()
plt.savefig(path_to_csv + '/' + "Timeless_shuffled_decision_tree.pdf", format="pdf", bbox_inches="tight")
plt.close()

# 8. textual rules
# rules_1 = export_text(
#     tree_1,
#     feature_names=list(feature_df.columns)
# )
# print(rules_1)
rules_2 = export_text(
    tree_2,
    feature_names=list(timeless_feature_df.columns)
)
print(rules_2)

# 9. features importance
# importance_1 = pd.DataFrame({
#     "feature": feature_df.columns,
#     "importance": tree_1.feature_importances_
# })
# importance_1 = importance_1.sort_values(
#     "importance",
#     ascending=False
# )
# print(importance_1.head(10))
importance_2 = pd.DataFrame({
    "feature": timeless_feature_df.columns,
    "importance": tree_2.feature_importances_
})
importance_2 = importance_2.sort_values(
    "importance",
    ascending=False
)
print(importance_2.head(10))
