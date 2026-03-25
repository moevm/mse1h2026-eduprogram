import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

export const fetchGraphData = async () => {
  try {
    const response = await axios.get(`${API_URL}/show-graph`);
    return response.data;
  } catch (error) {
    console.error('Error fetching graph data:', error);
    throw error;
  }
};