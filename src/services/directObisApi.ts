// Direct OBIS API Service - Bypasses backend completely
export const directObisService = {
  // Get OBIS datasets directly
  async getDatasets(limit: number = 20, offset: number = 0) {
    try {
      const response = await fetch(`https://api.obis.org/v3/dataset?limit=${limit}&offset=${offset}`);
      if (!response.ok) throw new Error(`OBIS API error: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching OBIS datasets:', error);
      throw error;
    }
  },

  // Get species occurrence data directly
  async getSpeciesOccurrence(scientificName: string, limit: number = 50) {
    try {
      const params = new URLSearchParams({
        scientificname: scientificName,
        limit: limit.toString()
      });
      const response = await fetch(`https://api.obis.org/v3/occurrence?${params}`);
      if (!response.ok) throw new Error(`OBIS API error: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching species occurrence:', error);
      throw error;
    }
  },

  // Get dataset occurrences directly
  async getDatasetOccurrences(datasetId: string, limit: number = 50) {
    try {
      const params = new URLSearchParams({
        datasetid: datasetId,
        limit: limit.toString()
      });
      const response = await fetch(`https://api.obis.org/v3/occurrence?${params}`);
      if (!response.ok) throw new Error(`OBIS API error: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching dataset occurrences:', error);
      throw error;
    }
  },

  // Get OBIS statistics directly
  async getStatistics() {
    try {
      const response = await fetch('https://api.obis.org/v3/statistics');
      if (!response.ok) throw new Error(`OBIS API error: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching OBIS statistics:', error);
      throw error;
    }
  },

  // Get taxon data directly
  async getTaxon(scientificName?: string) {
    try {
      const params = scientificName ? `?scientificname=${encodeURIComponent(scientificName)}` : '';
      const response = await fetch(`https://api.obis.org/v3/taxon${params}`);
      if (!response.ok) throw new Error(`OBIS API error: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching taxon data:', error);
      throw error;
    }
  },

  // Test OBIS connection
  async testConnection() {
    try {
      const response = await fetch('https://api.obis.org/v3/statistics');
      return {
        status: response.ok ? 'connected' : 'error',
        statusCode: response.status,
        message: response.ok ? 'OBIS API is accessible' : 'OBIS API connection failed'
      };
    } catch (error) {
      return {
        status: 'error',
        statusCode: 0,
        message: `Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }
};