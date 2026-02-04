"use client"

import { useEffect, useRef } from "react";
import { createChart,IChartApi, LineData } from "lightweight-charts";

type Props = {
    data: {time: number; value: number} [];
};
