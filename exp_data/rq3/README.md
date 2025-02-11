# RQ3 Data

## Overview

In the experiment for RQ3, we evaluated the bug detection capabilities of BugHunter on 237 popular apps randomly selected from Google Play, based on app type and download numbers. The experiment compared BugHunter with several baseline methods (Time-Machine, ComboDroid, APE+QT, Humanoid, GPTDroid), with all methods testing each app for 60 minutes.

Here are the relevant statistics for this part of the data:

| App categories | max activities | min activities | Median activities |
|-----------------|----------------|----------------|--------------------|
| 20             | 77             | 8              | 31                |

The results of the experiment are as follows:
1. BugHunter detected 93 crash bugs in 88 apps.
2. Among these, 49 bugs in 45 apps were discovered for the first time and had not been detected by any baseline method previously.
3. Of these newly discovered bugs, the best baseline, GPTDroid, detected only 7.
4. All bugs detected by the baseline methods were subsets of those detected by BugHunter.
5. We submitted these 49 newly discovered bugs to developers, and so far, 42 bugs have been fixed or confirmed (33 fixed, 9 confirmed, none rejected), with 7 still pending.

These data results indicate that BugHunter is highly effective in detecting unseen bugs and can uncover errors that other methods might miss.

## Confirmed Bugs

| ID | App name | Category | download | Version | Time-Machine | ComboDroid | APE+QT | Humanoid | GPTDroid |
|----|----------|----------|----------|---------|--------------|------------|---------|----------|----------|
| 1  | BOM Weather | weather | 1M+ | 6.9.1 |  |  |  |  |  |
| 2  | Weawow | weather | 5M+ | 6.2.8 |  |  |  |  |  |
| 3  | To-Do List | productivity | 10M+ | 10.3 |  |  |  |  |  |
| 4  | Roubit | productivity | 1M+ | 6.1.3 |  |  |  | ✅ |  |
| 5  | Bitget | finance | 5M+ | 2.41.3 |  |  |  |  |  |
| 6  | Tonkeeper | finance | 10M+ | 4.10.0 |  |  |  |  |  |
| 7  | Mi Fitness | health | 10M+ | 3.30.0 |  |  |  |  |  |
| 8  | Fitdays | health | 1M+ | 1.22.2 |  | ✅ |  |  |  |
| 9  | Tasty | food | 10M+ | 1.97.0 |  |  |  |  |  |


## Pending Bugs

| ID | App name       | Category | download | Version  | Time-Machine | ComboDroid | APE+QT | Humanoid | GPTDroid |
|----|---------------|----------|----------|----------|--------------|------------|---------|----------|----------|
| 1  | DoorDash      | food     | 50M+     | 15.18    |               |            |         |          |          |
| 2  | Daily Meal Planner | food     | 100K+    | 2.5.0    |               |            |         |          |          |
| 3  | Mindbody      | health   | 5M+      | 7.73.0   |               |            |         |          |          |
| 4  | FX File Explorer | business | 10M+     | 12.3     |               |            |         |          |          |
| 5  | App Sharer    | tool     | 10K+     | 1.0.4    |               |            |         |          |          |
| 6  | Send Anywhere  | productivity | 10M+     | 23.2.6   |               |            |         |          |          |
| 7  | Sportplan     | sport    | 50K+     | 3.0.38   |               |            |         |          |          |

## Fixed Bugs

| ID | App name | Category | Download | Version | TimeM | Comb | APE+QT | Humanoid | GPTDroid |
|-------------|-------------------|-------------------|-------------------|------------------|----------------|---------------|-----------------|-------------------|-------------------|
| 1           | Musixmatch        | music             | 50M+              | 7.10.1           |                |               |                 |                   |                   |
| 2           | Time Planner      | productivity      | 5M+               | 3.22             | ✅     | ✅    | ✅      |                   | ✅        |
| 3           | DailyLife         | lifestyle         | 5M+               | 4.3.0.2          |                |               |                 |                   |                   |
| 4           | Carousell         | shopping          | 10M+              | 2.370.4          |                |               |                 |                   |                   |
| 5           | Hungerstation     | food              | 10M+              | 8.0.19           |                |               |                 |                   |                   |
| 6           | Karrot            | social            | 10M+              | 24.33.0          |                |               |                 |                   |                   |
| 7           | Khan Academy      | education         | 10M+              | 8.1.0            |                |               |                 |                   |                   |
| 8           | Klook             | travel            | 10M+              | 7.3.1            | ✅     |               | ✅      | ✅        | ✅        |
| 9           | Money Manager     | finance           | 10M+              | 4.9.18           |                |               |                 |                   |                   |
| 10          | Musicolet         | music             | 10M+              | 11.3             |                |               |                 |                   |                   |
| 11          | Notion            | productivity      | 10M+              | 0.6.2419         |                |               |                 |                   |                   |
| 12          | Ringtones         | entertain         | 10M+              | 3.7.1            |                | ✅    |                 |                   | ✅        |
| 13          | School Planner    | education         | 10M+              | 8.2.1            | ✅     |               | ✅      | ✅        | ✅        |
| 14          | ShortMax          | entertain         | 10M+              | 1.9.1            |                |               |                 |                   |                   |
| 15          | Step Tracker      | health            | 10M+              | 1.4.7            |                |               |                 |                   |                   |
| 16          | To-Do List        | productivity      | 10M+              | 3.7.1            |                | ✅    |                 |                   |                   |
| 17          | Transit           | map               | 10M+              | 5.15.1           |                |               |                 |                   |                   |
| 18          | Zepp              | sport             | 10M+              | 8.12.3           |                |               |                 |                   |                   |
| 19          | BetterMe          | health            | 1M+               | 4.54.0           |                |               |                 |                   |                   |
| 20          | Cathay            | finance           | 1M+               | 5.14.1           |                |               | ✅      | ✅        |                   |
| 21          | Coupang           | shopping          | 1M+               | 8.3.1            |                | ✅    |                 |                   | ✅        |
| 22          | Drink Water       | health            | 1M+               | 1.102.19         |                |               |                 |                   |                   |
| 23          | eSound            | music             | 1M+               | 4.11.1           |                |               |                 |                   |                   |
| 24          | Fortune City      | finance           | 1M+               | 4.6.1            |                |               |                 |                   |                   |
| 25          | Home Assistant    | house             | 1M+               | 4.3.0            |                |               | ✅      |                   | ✅        |
| 26          | MTR Mobile        | travel            | 1M+               | 20.39.1          |                |               |                 |                   |                   |
| 27          | Rabit             | productivity      | 1M+               | 4.1.362          |                |               |                 |                   |                   |
| 28          | Zenmoney          | finance           | 1M+               | 7.9.0            |                |               |                 |                   |                   |
| 29          | MyTranslink       | map               | 500K+             | 3.7.12345        |                |               |                 |                   |                   |
| 30          | New Scientist     | news              | 500K+             | 4.9              |                |               |                 |                   |                   |
| 31          | Turbo Alarm       | tool              | 500K+             | 17.3             |                |               |                 |                   | ✅        |
| 32          | CodeSnack         | education         | 100K+             | 5.5.1            |                |               |                 |                   |                   |
| 33          | FilterBox         | tool              | 100K+             | 3.3.3            |                |               |                 |                   |                   |
