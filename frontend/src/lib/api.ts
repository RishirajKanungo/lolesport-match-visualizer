// src/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Region {
  code: string;
  name: string;
  region: string;
}

export interface Tournament {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
}

export async function fetchRegions(): Promise<Region[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/regions`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching regions:", error);
    return [];
  }
}

export async function fetchYears(): Promise<number[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/years`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching years:", error);
    return [];
  }
}

export async function fetchTournaments(
  regionCode: string,
  year: string
): Promise<Tournament[]> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/tournaments?region_code=${regionCode}&year=${year}`
    );
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching tournaments:", error);
    return [];
  }
}
