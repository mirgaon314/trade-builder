export type Ticker = {
  symbol: string;
  name: string;
  exchange: string;   // NASDAQ, NYSE, etc.
  type: "stock" | "index" | "etf" | "crypto";
};

export const UNIVERSE: Ticker[] = [
  { symbol: "AAPL", name: "Apple Inc.", exchange: "NASDAQ", type: "stock" },
  { symbol: "MSFT", name: "Microsoft Corporation", exchange: "NASDAQ", type: "stock" },
  { symbol: "NVDA", name: "NVIDIA Corporation", exchange: "NASDAQ", type: "stock" },
  { symbol: "AMZN", name: "Amazon.com, Inc.", exchange: "NASDAQ", type: "stock" },
  { symbol: "GOOGL", name: "Alphabet Inc. (Class A)", exchange: "NASDAQ", type: "stock" },
  { symbol: "TSLA", name: "Tesla, Inc.", exchange: "NASDAQ", type: "stock" },
  { symbol: "NFLX", name: "Netflix, Inc.", exchange: "NASDAQ", type: "stock" },
  { symbol: "NKE",  name: "Nike, Inc.", exchange: "NYSE", type: "stock" },
  { symbol: "^NDX", name: "NASDAQ 100 Index", exchange: "INDEX", type: "index" },
  { symbol: "SPY",  name: "SPDR S&P 500 ETF", exchange: "NYSE Arca", type: "etf" },
];