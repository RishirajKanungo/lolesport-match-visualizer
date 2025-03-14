// src/components/FilterPanel.tsx (fixed region selection)
"use client";

import React, { useState, useEffect } from "react";
import {
  fetchRegions,
  fetchYears,
  fetchTournaments,
  Region,
  Tournament,
} from "@/lib/api";

interface FilterPanelProps {
  onFilterChange: (filters: {
    regionCode: string;
    year: string;
    tournamentId: string;
  }) => void;
}

export default function FilterPanel({ onFilterChange }: FilterPanelProps) {
  const [regions, setRegions] = useState<Region[]>([]);
  const [years, setYears] = useState<number[]>([]);
  const [tournaments, setTournaments] = useState<Tournament[]>([]);

  const [selectedRegion, setSelectedRegion] = useState<string>("");
  const [selectedYear, setSelectedYear] = useState<string>("");
  const [selectedTournament, setSelectedTournament] = useState<string>("");

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [loadingTournaments, setLoadingTournaments] = useState<boolean>(false);

  // Fetch regions and years on component mount
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setIsLoading(true);
        const [regionsData, yearsData] = await Promise.all([
          fetchRegions(),
          fetchYears(),
        ]);

        if (regionsData.length > 0) {
          console.log("Loaded regions:", regionsData);
          // Fix regions with empty codes
          const fixedRegions = regionsData.map((region, index) => {
            if (!region.code) {
              // Use the league name to generate a code
              const words = region.name.split(" ");
              const generatedCode = words
                .map((word) => word[0])
                .join("")
                .toUpperCase();
              return { ...region, code: generatedCode || `REGION${index}` };
            }
            return region;
          });

          setRegions(fixedRegions);
        }

        if (yearsData.length > 0) {
          console.log("Loaded years:", yearsData);
          setYears(yearsData);
        }

        setIsLoading(false);
      } catch (error) {
        console.error("Error loading initial data:", error);
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, []);

  // Fetch tournaments when region or year changes
  useEffect(() => {
    const loadTournaments = async () => {
      if (selectedRegion && selectedYear) {
        try {
          setLoadingTournaments(true);
          console.log(
            `Fetching tournaments for region: ${selectedRegion}, year: ${selectedYear}`
          );

          const tournamentsData = await fetchTournaments(
            selectedRegion,
            selectedYear
          );
          console.log("Loaded tournaments:", tournamentsData);

          setTournaments(tournamentsData);
          setSelectedTournament("");
          setLoadingTournaments(false);
        } catch (error) {
          console.error("Error loading tournaments:", error);
          setTournaments([]);
          setLoadingTournaments(false);
        }
      } else {
        setTournaments([]);
      }
    };

    loadTournaments();
  }, [selectedRegion, selectedYear]);

  // Handle region selection
  const handleRegionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    console.log("Selected region:", value);
    setSelectedRegion(value);
    // Reset tournament when region changes
    setSelectedTournament("");
  };

  // Handle year selection
  const handleYearChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    console.log("Selected year:", value);
    setSelectedYear(value);
    // Reset tournament when year changes
    setSelectedTournament("");
  };

  // Handle tournament selection
  const handleTournamentChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    console.log("Selected tournament:", value);
    setSelectedTournament(value);

    // Notify parent component when all selections are made
    if (selectedRegion && selectedYear && value) {
      onFilterChange({
        regionCode: selectedRegion,
        year: selectedYear,
        tournamentId: value,
      });
    }
  };

  return (
    <div className="filter-panel p-4 bg-gray-100 rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4 text-gray-800">Match Filters</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Region Dropdown */}
        <div className="filter-group">
          <label
            htmlFor="region-select"
            className="block mb-2 font-medium text-gray-800"
          >
            Region
          </label>
          <select
            id="region-select"
            className="w-full p-2 border rounded bg-white text-gray-800"
            value={selectedRegion}
            onChange={handleRegionChange}
            disabled={isLoading}
          >
            <option value="">Select Region</option>
            {regions.map((region, index) => {
              // Generate a display name using code if available, otherwise just the name
              const displayText = region.code
                ? `${region.code} (${region.name})`
                : region.name;

              // Use name as value if code is empty
              const valueToUse = region.code || `region-${index}`;

              return (
                <option key={`region-${index}`} value={valueToUse}>
                  {displayText}
                </option>
              );
            })}
          </select>
        </div>

        {/* Year Dropdown */}
        <div className="filter-group">
          <label
            htmlFor="year-select"
            className="block mb-2 font-medium text-gray-800"
          >
            Year
          </label>
          <select
            id="year-select"
            className="w-full p-2 border rounded bg-white text-gray-800"
            value={selectedYear}
            onChange={handleYearChange}
            disabled={isLoading}
          >
            <option value="">Select Year</option>
            {years.map((year, index) => (
              <option key={`year-${index}`} value={year.toString()}>
                {year}
              </option>
            ))}
          </select>
        </div>

        {/* Tournament Dropdown */}
        <div className="filter-group">
          <label
            htmlFor="tournament-select"
            className="block mb-2 font-medium text-gray-800"
          >
            Tournament
          </label>
          <select
            id="tournament-select"
            className="w-full p-2 border rounded bg-white text-gray-800"
            value={selectedTournament}
            onChange={handleTournamentChange}
            disabled={!selectedRegion || !selectedYear || loadingTournaments}
          >
            <option value="">
              {loadingTournaments
                ? "Loading tournaments..."
                : tournaments.length === 0 && selectedRegion && selectedYear
                ? "No tournaments found"
                : "Select Tournament"}
            </option>
            {tournaments.map((tournament, index) => (
              <option key={`tournament-${index}`} value={tournament.id}>
                {tournament.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Debug info - remove in production */}
      <div className="mt-4 p-2 bg-gray-200 rounded text-sm">
        <p>Selected Region: {selectedRegion || "None"}</p>
        <p>Selected Year: {selectedYear || "None"}</p>
        <p>Selected Tournament: {selectedTournament || "None"}</p>
      </div>
    </div>
  );
}
