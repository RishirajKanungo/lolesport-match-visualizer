// src/app/page.tsx
"use client";

import { useState } from "react";
import FilterPanel from "@/components/FilterPanel";

export default function Home() {
  const [filters, setFilters] = useState<{
    regionCode: string;
    year: string;
    tournamentId: string;
  } | null>(null);

  const handleFilterChange = (newFilters: {
    regionCode: string;
    year: string;
    tournamentId: string;
  }) => {
    setFilters(newFilters);
    // Later we can use these filters to fetch matches
  };

  return (
    <main className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">LoL Match Visualizer</h1>

      <FilterPanel onFilterChange={handleFilterChange} />

      {filters && (
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h2 className="text-xl font-bold mb-2">Selected Filters:</h2>
          <p>
            <strong>Region:</strong> {filters.regionCode}
          </p>
          <p>
            <strong>Year:</strong> {filters.year}
          </p>
          <p>
            <strong>Tournament:</strong> {filters.tournamentId}
          </p>
        </div>
      )}
    </main>
  );
}
