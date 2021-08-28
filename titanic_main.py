# # -*- coding: utf-8 -*-
# """titanic_main.ipynb

# Automatically generated by Colaboratory.

# Original file is located at
#     https://colab.research.google.com/drive/1zt1cnhF8Mxm2y9SXkaEKflZEufveBh2o
# """

# import os
# # Find the latest version of spark 3.0  from http://www-us.apache.org/dist/spark/ and enter as the spark version
# # For example:
# # spark_version = 'spark-3.0.2'
# spark_version = 'spark-3.1.2'
# os.environ['SPARK_VERSION']=spark_version

# # Install Spark and Java
# !apt-get update
# !apt-get install openjdk-11-jdk-headless -qq > /dev/null
# !wget -q https://downloads.apache.org/spark/$SPARK_VERSION/$SPARK_VERSION-bin-hadoop2.7.tgz
# !tar xf $SPARK_VERSION-bin-hadoop2.7.tgz
# !pip install -q findspark

# # Set Environment Variables
# os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
# os.environ["SPARK_HOME"] = f"/content/{spark_version}-bin-hadoop2.7"

# # Start a SparkSession
# import findspark
# findspark.init()

# !wget https://jdbc.postgresql.org/download/postgresql-42.2.9.jar

# # Commented out IPython magic to ensure Python compatibility.
# # %matplotlib inline
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd

# from pyspark.sql import SparkSession
# spark = SparkSession.builder.appName("CloudETL").config("spark.driver.extraClassPath","/content/postgresql-42.2.9.jar").getOrCreate()

# # Read in data from S3 Buckets
# from pyspark import SparkFiles

# # test data
# url="https://data-bootcamp-titanic.s3.us-east-2.amazonaws.com/test.csv"
# spark.sparkContext.addFile(url)
# test_df = spark.read.csv(SparkFiles.get("test.csv"), sep=",", header=True, inferSchema=True)

# # train data
# url="https://data-bootcamp-titanic.s3.us-east-2.amazonaws.com/train.csv"
# spark.sparkContext.addFile(url)
# train_df = spark.read.csv(SparkFiles.get("train.csv"), sep=",", header=True, inferSchema=True)


import os
import boto3

# Show DataFrame
test_df.show()
train_df.show()

# Convert pyspark dataframes to pandas
pd_train_df = train_df.toPandas()
pd_test_df = test_df.toPandas()

"""# Begin Machine Learning

## Univariate Linear Regression Models
"""

from sklearn.linear_model import LinearRegression

# Linear Regression of Age
age_data = pd_train_df.copy()

# drop nas from Age column
age_data = age_data[age_data['Age'].notna()]

# assign data to X and y
X = age_data["Age"].values.reshape(-1,1)
y = age_data["Survived"].values.reshape(-1,1)

plt.scatter(X,y)

"""### upon making the above 'model' I realized linear regression doesn't make sense. Moving on to logistical models. We can also tell that age isn't a good predictor of survival alone

# Logistic Regression
"""

# Logistic Regression 
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(solver='liblinear')

# Create X_train and y_train
X_train = pd_train_df.drop(["PassengerId","Ticket","Cabin", "Name", "Embarked"], axis=1)
X_train = X_train.dropna()
y_train = X_train["Survived"]
X_train = X_train.drop(["Survived"], axis=1)

# Create X_test
X_test = pd_test_df.drop(["PassengerId","Ticket","Cabin", "Name", "Embarked"], axis=1)
X_test = X_test.dropna()

# Encode Sex and Passenger Class
X_train = pd.get_dummies(X_train, columns=["Sex", "Pclass"])
X_test = pd.get_dummies(X_test, columns=["Sex", "Pclass"])

# Bin Fare for encoding
bins = [0, 8.05, 15.7417, 33.375, 100, 513]
labels = ["cheapest", "cheap", "medium", "expensive", "most expensive"]
X_train["Fare cat."] = pd.cut(X_train["Fare"], bins, labels=labels)
X_test["Fare cat."] = pd.cut(X_test["Fare"], bins, labels=labels)

# Encode Fare
X_train = pd.get_dummies(X_train, columns=["Fare cat."])
X_test = pd.get_dummies(X_test, columns=["Fare cat."])

# drop Fare columns
X_train = X_train.drop(columns=["Fare", "Parch", "SibSp"])
X_test = X_test.drop(columns=["Fare", "Parch", "SibSp"])

X_train.head(1)

X_test.head(1)

clf.fit(X_train,y_train)

print(f"Training Data Score: {clf.score(X_train, y_train)}")

"""# IT'S BETTER THAN RANDOM"""

predictions = clf.predict(X_train)
pred_df = pd.DataFrame({
    "Age": X_train["Age"],
    "Sex_female": X_train["Sex_female"],
    "Sex_male":	X_train["Sex_male"],
    "Pclass_1": X_train["Pclass_1"],
    "Pclass_2": X_train["Pclass_2"],
    "Pclass_3":	X_train["Pclass_3"],
    "Fare-cheapest": X_train["Fare cat._cheapest"],
    "Fare-cheap": X_train[ "Fare cat._cheap"],
    "Fare-medium": X_train["Fare cat._medium"],
    "Fare-expensive": X_train[ "Fare cat._expensive"],
    "Fare-most expensive": X_train["Fare cat._most expensive"],
    "[Prediction": predictions, 
    "Actual]": y_train
    }).reset_index(drop=True)
pred_df.head(20)

wrong_df = pred_df.loc[pred_df["[Prediction"] != pred_df["Actual]"],:]
wrong_indexi = wrong_df.index
pd_train_df.iloc[wrong_indexi,:]

"""#### Print out pd_train_df then X_train to make sure indexing stayed consistent when transforming"""

pd_train_df.head()

X_train.head()

"""# STOPPED HERE
next steps: 
  - bin ages and add to model (bins below) ; keep this model above for comparison
  - explore KNN and tree models
"""

# # Bin Ages so Hot Coding can be done
# bins = [0, 1, 4, 12, 19, 30, 65, 80]
# labels = ["infant", "toddler", "child", "teenager", "young adult", "adult", "elder"]
# X["Age Range"] = pd.cut(X["Age"], bins, labels=labels)
