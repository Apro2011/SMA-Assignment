# Imports
import pandas as pd
import plotly.express as px
import numpy as np
import psycopg2
import decimal


# Database Connection
conn = psycopg2.connect(
    database="investo_database",
    user="investo_user",
    password="investo_password",
    host="127.0.0.1",
    port="5432",
)

cursor = conn.cursor()

cursor.execute("SELECT * FROM HINDALCO_TABLE")

# SMA settings
fsma_period = 10  # Fast SMA Period
ssma_period = 100  # Slow SMA Period

# Getting Historical Data
bars = cursor.fetchall()
df = pd.DataFrame(
    bars, columns=["datetime", "close", "high", "low", "open", "volume", "instrument"]
)
df["fast_sma"] = df["close"].rolling(fsma_period).mean().astype(float)
df["slow_sma"] = df["close"].rolling(ssma_period).mean().astype(float)
df["prev_fast_sma"] = df["fast_sma"].shift(1).astype(float)
df.dropna(inplace=True)


# Finding crossovers
def find_crossover(fast_sma, prev_fast_sma, slow_sma):
    """Finding Crossover Logic"""
    if fast_sma > slow_sma and prev_fast_sma < slow_sma:
        return "bullish crossover"
    elif fast_sma < slow_sma and prev_fast_sma > slow_sma:
        return "bearish crossover"
    else:
        return None


df["crossover"] = np.vectorize(find_crossover)(
    df["fast_sma"], df["prev_fast_sma"], df["slow_sma"]
)
signal = df[df["crossover"] == "bullish crossover"].copy()


# Creating backtest of position and strategy classes
class Position:
    """Backtest Position"""

    def __init__(
        self, open_datetime, open_price, order_type, volume, sl_percent, tp_percent
    ):
        self.open_datetime = open_datetime
        self.open_price = open_price
        self.order_type = order_type
        self.volume = volume
        self.sl_percent = sl_percent
        self.tp_percent = tp_percent
        self.close_datetime = None
        self.close_price = None
        self.profit = None
        self.status = "open"

    def close_position(self, close_datetime, close_price):
        """Close Position Details"""
        self.close_datetime = close_datetime
        self.close_price = close_price
        self.profit = (
            (self.close_price - self.open_price) * self.volume
            if self.order_type == "buy"
            else (self.open_price - self.close_price) * self.volume
        )
        self.status = "closed"

    def check_stop_loss_take_profit(self, high, low):
        """Check if stop-loss or take-profit conditions are met"""
        if self.order_type == "buy" and low <= self.open_price * (1 - self.sl_percent):
            return "stop-loss"
        elif self.order_type == "sell" and high >= self.open_price * (
            1 + self.tp_percent
        ):
            return "take-profit"
        else:
            return None

    def _asdict(self):
        return {
            "open_datetime": self.open_datetime,
            "open_price": self.open_price,
            "order_type": self.order_type,
            "volume": self.volume,
            "sl_percent": self.sl_percent,
            "tp_percent": self.tp_percent,
            "close_datetime": self.close_datetime,
            "close_price": self.close_price,
            "profit": self.profit,
            "status": self.status,
        }


class Strategy:
    """Backtesting Strategy"""

    def __init__(self, df, starting_balance, sl_percent, tp_percent):
        self.starting_balance = starting_balance
        self.balance = starting_balance
        self.positions = []
        self.data = df
        self.sl_percent = sl_percent
        self.tp_percent = tp_percent

    def get_positions_df(self):
        """Getting Positions data"""
        df = pd.DataFrame([position._asdict() for position in self.positions])
        df["pnl"] = df["profit"].cumsum() + self.starting_balance
        return df

    def add_position(self, position):
        """Adding positions"""
        self.positions.append(position)
        return True

    def run(self):
        for i, data in self.data.iterrows():
            if data.crossover == "bearish crossover":
                for position in self.positions:
                    if position.status == "open":
                        position.close_position(data.datetime, data.close)

            if data.crossover == "bullish crossover":
                # Use high and low prices to set stop-loss and take-profit levels
                sl_percent = self.sl_percent
                tp_percent = self.tp_percent

                self.add_position(
                    Position(
                        data.datetime,
                        data.close,
                        "buy",
                        data.volume,
                        sl_percent,
                        tp_percent,
                    )
                )

                # Check stop-loss and take-profit conditions for existing positions
                for position in self.positions:
                    stop_or_take = position.check_stop_loss_take_profit(
                        data.high, data.low
                    )
                    if stop_or_take == "stop-loss" or stop_or_take == "take-profit":
                        position.close_position(data.datetime, data.close)

        return self.get_positions_df()


# Run the backtest
sma_crossover_strategy = Strategy(
    df,
    starting_balance=10000,
    sl_percent=decimal.Decimal(0.02),
    tp_percent=decimal.Decimal(0.05),
)
result = sma_crossover_strategy.run()

print(result)

# Visualize
new_fig = px.line(result, x="close_datetime", y="pnl")
new_fig.show()

df_long = pd.melt(
    df,
    id_vars=["datetime"],
    value_vars=["close", "fast_sma", "slow_sma"],
    var_name="variable",
    value_name="value",
)

fig = px.line(
    df_long,
    x="datetime",
    y="value",
    color="variable",
    labels={"value": "Value", "variable": "Variable"},
    title="Line Plot of Close, Fast SMA, and Slow SMA",
)

for i, row in signal.iterrows():
    fig.add_vline(x=row.datetime)

for (
    i,
    row,
) in result[result["status"] == "closed"].iterrows():
    if row.profit > 0:
        fig.add_shape(
            type="line",
            x0=row.open_datetime,
            y0=row.open_price,
            x1=row.close_datetime,
            y1=row.close_price,
            line=dict(color="Green", width=3),
        )

    elif row.profit < 0:
        fig.add_shape(
            type="line",
            x0=row.open_datetime,
            y0=row.open_price,
            x1=row.close_datetime,
            y1=row.close_price,
            line=dict(color="Red", width=3),
        )

fig.show()
