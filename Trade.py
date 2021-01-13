class Trade:

    conversion = {
        "USD_JPY": [0.001],
        "EUR_USD": [0.001],
        "XAU_USD": [0.0025],
        "EUR_JPY": [0.0016],
        "GBP_USD": [0.001],
        "US30_USD": [0.001],
    }

    def __init__(
        self,
        market,
        openP,
        capital,
        spread,
        rates,
        commission=0,
    ):
        for name in self.conversion:
            if "JPY" in name:
                self.conversion[name].append(rates["JPY"])
            elif "USD" in name:
                self.conversion[name].append(rates["USD"])

        self.market = market.upper()
        if self.market == "USD_JPY" or self.market == "EUR_JPY":
            self.openP = openP * 100
        elif self.market == "US30_USD":
            self.openP = openP
        if self.market == "XAU_USD":
            self.openP = openP * 10
        else:
            self.openP = openP * 10000
        self.commision = commission
        self.capital = capital
        self.multiplier = self.conversion[self.market][0]
        self.uk = Trade.conversion[market][1]
        self.risk = 0.024 / len(Trade.conversion)
        self.spread = spread

    def units(self):
        change = self.buyP()[1] - self.buy_sl()[1]
        lots = ((self.capital * self.risk) / (change + self.commision)) * self.uk
        if self.market == "XAU_USD":
            return round(lots * 10, 0)
        elif self.market == "US30_USD":
            return round(lots * 10000, 0)
        elif self.market == "USD_JPY" or self.market == "EUR_JPY":
            return round(lots * 1000000, 0)
        return round(lots * 10000, 0)

    def buyP(self):
        if self.market == "USD_JPY" or self.market == "EUR_JPY":
            return (
                round((self.openP * (1 + self.multiplier)) / 10000, 3),
                self.openP * (1 + self.multiplier),
            )
        elif self.market == "US30_USD":
            return round(self.openP * (1 + self.multiplier) / 10000, 0), self.openP * (
                1 + self.multiplier
            )
        elif self.market == "XAU_USD":
            return round(self.openP * (1 + self.multiplier) / 10, 1), self.openP * (
                1 + self.multiplier
            )
        return round(self.openP * (1 + self.multiplier) / 10000, 5), self.openP * (
            1 + self.multiplier
        )

    def buy_tp(self):
        if self.market == "USD_JPY" or self.market == "EUR_JPY":
            return round(
                (self.openP + 6.25 * ((self.openP * self.multiplier) + self.spread))
                / 10000,
                3,
            )
        elif self.market == "US30_USD":
            return round(
                (self.openP + 6.25 * ((self.openP * self.multiplier) + self.spread))
                / 10000,
                1,
            )
        elif self.market == "XAU_USD":
            return round(
                (self.openP + 6.25 * ((self.openP * self.multiplier) + self.spread))
                / 10,
                1,
            )
        return round(
            (self.openP + 6.25 * ((self.openP * self.multiplier) + self.spread))
            / 10000,
            5,
        )

    def buy_sl(self):
        if self.market == "USD_JPY" or self.market == "EUR_JPY":
            return (
                round((self.openP - self.spread) / 10000, 3),
                self.openP - self.spread,
            )
        elif self.market == "US30_USD":
            return (
                round((self.openP - self.spread) / 10000, 1),
                self.openP - self.spread,
            )
        elif self.market == "XAU_USD":
            return round((self.openP - self.spread) / 10, 1), self.openP - self.spread
        return round((self.openP - self.spread) / 10000, 5), self.openP - self.spread

    def sellP(self):
        if self.market == "USD_JPY" or self.market == "EUR_JPY":
            return round(
                ((self.openP * (1 - self.multiplier)) - self.spread) / 10000, 3
            )
        elif self.market == "US30_USD":
            return round(
                ((self.openP * (1 - self.multiplier)) - self.spread) / 10000, 1
            )
        elif self.market == "XAU_USD":
            return round(((self.openP * (1 - self.multiplier)) - self.spread) / 10, 1)
        return round(((self.openP * (1 - self.multiplier)) - self.spread) / 10000, 5)

    def sell_tp(self):
        if self.market == "USD_JPY" or self.market == "EUR_JPY":
            return round(
                (self.openP - 6.25 * ((self.openP * self.multiplier) + self.spread))
                / 10000,
                3,
            )
        elif self.market == "US30_USD":
            return round(
                (self.openP - 6.25 * ((self.openP * self.multiplier) + self.spread))
                / 10000,
                1,
            )
        elif self.market == "XAU_USD":
            return round(
                (self.openP - 6.25 * ((self.openP * self.multiplier) + self.spread))
                / 10,
                1,
            )
        return round(
            (self.openP - 6.25 * ((self.openP * self.multiplier) + self.spread))
            / 10000,
            5,
        )

    def sell_sl(self):
        if self.market == "USD_JPY" or self.market == "EUR_JPY":
            return round(self.openP / 10000, 3)
        elif self.market == "US30_USD":
            return round(self.openP / 10000, 1)
        elif self.market == "XAU_USD":
            return round(self.openP / 10, 1)
        return round(self.openP / 10000, 5)


if __name__ == "__main__":
    market = input("market: ")
    openP = float(input("open price: "))
    capital = float(input("capital: "))
    spread = float(input("spread:"))

    trade1 = Trade(market, openP, capital, spread)
    print("buy:")
    print(
        f"units: {trade1.units()} price: {trade1.buyP()[0]} take profit: {trade1.buy_tp()} stop loss: {trade1.buy_sl()[0]}"
    )
    print("sell:")
    print(
        f"lots: {trade1.units()} price: {trade1.sellP()} take profit: {trade1.sell_tp()} stop loss: {trade1.sell_sl()}"
    )
