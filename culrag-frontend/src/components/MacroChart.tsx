import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { Macros } from "../types";

interface MacroChartProps {
  macros: Macros;
}

const COLORS = {
  Protein: "#DC2626", // red
  Carbs: "#2563EB", // blue
  Fat: "#F59E0B", // yellow
};

/** Pie chart of the protein/carbs/fat split, with percentages in the legend. */
export default function MacroChart({ macros }: MacroChartProps) {
  const total = macros.protein_g + macros.carbs_g + macros.fat_g || 1;
  const data = [
    { name: "Protein", value: macros.protein_g },
    { name: "Carbs", value: macros.carbs_g },
    { name: "Fat", value: macros.fat_g },
  ];

  return (
    <div className="h-56 w-full" aria-label="Macronutrient breakdown chart">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={40} outerRadius={70}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name as keyof typeof COLORS]} />
            ))}
          </Pie>
          <Tooltip formatter={(value: number) => `${value.toFixed(1)}g`} />
          <Legend
            formatter={(name: string) => {
              const entry = data.find((d) => d.name === name);
              const pct = entry ? ((entry.value / total) * 100).toFixed(0) : "0";
              return `${name} ${pct}%`;
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
