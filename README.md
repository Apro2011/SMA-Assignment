# Way to run the assignment

## Package and Environment Setup
1. Just run "pipenv install" and then "pipenv shell" commands, and let the packages and enviroenment set up.

## Data upload
1. Create postgresql role with name "investo_user", password "investo_password", database_name "investo_database".
2. Then run the data_upload.py file with "python data_upload.py" command, and let the data upload in database table.

## Main code
1. Run "python sma_strategy.py" to run the data analysis and sma strategy creation.

## Unit Tests
1. Run "pytest test_inputs.py" to run the input validation tests.
<video src="Visualize%20crossover.mp4" controls title="Visualize Crossover"></video>
<video src="Visualize%20Backtest.mp4" controls title="Visualize Backtest"></video>
![Backtest Results](<Backtest Results.png>)
![Bullish Crossover Signal](<Bullish Crossover Signal.png>)