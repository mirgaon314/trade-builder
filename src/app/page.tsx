"use client";

import { useState } from "react";
import SearchBar from "@/components/SearchBar";

export default function Home() {
  const [symbol, setSymbol] = useState<string | null>(null);

  return (
    <main className="min-h-screen bg-gray-950 text-white p-6">
      <div className="mx-auto max-w-5xl space-y-6">
        <h1 className="text-3xl font-bold">Trading Algorithm Builder</h1>

        <SearchBar onSearch={(s) => setSymbol(s)} />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <section className="md:col-span-2 rounded-2xl border border-gray-800 p-4">
            <h2 className="font-semibold mb-2">Price Chart</h2>
            <div className="h-64 flex items-center justify-center text-gray-400">
              {symbol ? `Ready to load ${symbol}…` : "Search a ticker to begin"}
            </div>
          </section>

          <aside className="rounded-2xl border border-gray-800 p-4 space-y-4">
            <h3 className="font-semibold">Prediction & Model</h3>
            <div className="text-sm text-gray-300">
              (Coming next) We’ll show a prediction line and simple model controls here.
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}