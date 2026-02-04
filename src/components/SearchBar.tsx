"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { UNIVERSE } from "@/lib/temp_universe";

type Props = {
    onSearch: (symbol: string) => void
};

export default function SearchBar({onSearch}: Props){
    const [value, setValue] = useState("");
    const [open, setOpen] = useState(false);            // control visibility
    const wrapRef = useRef<HTMLDivElement>(null);       // detect outside clicks

    // compute matches whenever the input changes
    const matches = useMemo(() =>{
        const s = value.trim().toUpperCase();
        if (!s) return [];
        return UNIVERSE.filter(
            t => t.symbol.startsWith(s) || t.name.toUpperCase().includes(s)
        ).slice(0, 8);
    }, [value]);

    useEffect(() => {
        function onDocClick(e: MouseEvent) {
            if (!wrapRef.current) return;
            if (!wrapRef.current.contains(e.target as Node)) setOpen(false);
        }
        function handleEscKey(e:KeyboardEvent) {
            if (e.key === 'Escape') setOpen(false);
        }
        document.addEventListener("mousedown",onDocClick);
        document.addEventListener("keydown",handleEscKey);
        return () => {
            document.removeEventListener("mousedown", onDocClick);
            document.removeEventListener("keydown",handleEscKey);
        };
    }, []);


    const submit = (e: React.FormEvent) => {
        e.preventDefault();
        const s = value.trim().toUpperCase();
        if (!s) return;
        onSearch(s);
        setOpen(false);
    };

    const pick = (symbol: string) => {
        setValue(symbol);
        onSearch(symbol);
        setOpen(false);
    };

    return (
        <div ref={wrapRef} className="relative w-full">
            <form onSubmit={submit} className="w-full flex gap-2">
            <input
                className="flex-1 rounded-xl border border-gray-700 bg-gray-900/50 p-3 text-white"
                placeholder="Search ticker (e.g., AAPL, MSFT)…"
                value={value}
                onFocus={() => setOpen(true)}
                onChange={(e) => {
                    setValue(e.target.value);
                    setOpen(true);
                }}
            />
            <button
                type="submit"
                className="rounded-xl bg-white/10 px-4 py-2 text-white hover:bg-white/20"
            >
                Search
            </button>
            </form>

            {open && matches.length > 0 && (
                <div className="absolute z-10 mt-2 w-full overflow-hidden rounded-xl border border-gray-700 bg-gray-900/95 shadow-lg backdrop-blur">
                    {matches.map((t) => (
                        <button
                            key = {t.symbol}
                            onClick={() => pick(t.symbol)}
                            className = "flex w-full items-center gap-3 px-3 py-2 text-left hover:bg-white/10"
                        >
                            <div className="min-w-[64px] font-semibold">{t.symbol}</div>
                            <div className="flex-1 text-sm text-gray-300 truncate">{t.name}</div>
                            <div className="text-xs text-gray-400">{t.exchange}</div>
                        </button>
                    ))}
                </div>
            )}

            {open && matches.length === 0 && value && (
                <div className="absolute z-10 mt-2 w-full overflow-hidden rounded-xl border border-gray-700 bg-gray-900/95 shadow-lg backdrop-blur">
                    <div className ="min-w-[64px] font-semibold gap-3 px-3 py-2 text-left">no results</div>
                </div>
            )}
        </div>
    );
}

