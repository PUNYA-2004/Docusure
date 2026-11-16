import React from "react";

export default function MetricCard({ title, value, subtitle, icon: Icon, color = "blue", badge }) {
  const colorMap = {
    blue: "from-blue-500/10 to-indigo-500/5 text-blue-400 border-blue-500/20",
    emerald: "from-emerald-500/10 to-teal-500/5 text-emerald-400 border-emerald-500/20",
    amber: "from-amber-500/10 to-orange-500/5 text-amber-400 border-amber-500/20",
    rose: "from-rose-500/10 to-pink-500/5 text-rose-400 border-rose-500/20",
    purple: "from-purple-500/10 to-indigo-500/5 text-purple-400 border-purple-500/20",
  };

  const currentTheme = colorMap[color] || colorMap.blue;

  return (
    <div className={`glass-panel p-5 rounded-xl border bg-gradient-to-br ${currentTheme} transition-all duration-300 hover:scale-[1.01]`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-bold text-white mt-1 font-mono">{value}</h3>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className="flex flex-col items-end space-y-2">
          {Icon && (
            <div className="p-2.5 rounded-lg bg-gray-900/60 border border-white/5">
              <Icon className="w-5 h-5" />
            </div>
          )}
          {badge && (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-white/10 text-gray-200">
              {badge}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
