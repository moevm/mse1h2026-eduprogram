import { fetchWithAuth } from './httpClient';

const domain = process.env.REACT_APP_API_URL || 'localhost:8000';
const API_BASE_URL = domain.startsWith('http') ? domain : `http://${domain}`;

const normalizeGraphIdComponent = (value) => {
  const specialSymbols = ['~', '.', '-', '!', '$', '&', "'", '(', ')', '*', '+', ',', ';', '=', '?', '#', '@', '%', '№', '>', '<'];

  let result = String(value || '').trim();
  result = result.replace(/ /g, '_');
  result = result.replace(/\//g, '_');
  result = result.replace(/,/g, '_');

  specialSymbols.forEach((symbol) => {
    result = result.replaceAll(symbol, `\\${symbol}`);
  });

  result = result.replaceAll('«', '');
  result = result.replaceAll('»', '');

  return result;
};

export const buildGraphId = (userId, programFolder, universityName) => {
  const resolvedUniversity = normalizeGraphIdComponent(`${universityName || 'frontend'} id ${userId}`);
  const resolvedProgram = normalizeGraphIdComponent(programFolder);

  return `${resolvedUniversity}/${resolvedProgram}`;
};

const normalizeDisciplines = (disciplinesRaw) => {
  if (Array.isArray(disciplinesRaw)) {
    return disciplinesRaw.reduce((acc, disciplineItem) => {
      if (!disciplineItem || typeof disciplineItem !== 'object' || Array.isArray(disciplineItem)) {
        return acc;
      }

      Object.entries(disciplineItem).forEach(([disciplineName, disciplineData]) => {
        acc[disciplineName] = disciplineData;
      });

      return acc;
    }, {});
  }

  if (disciplinesRaw && typeof disciplinesRaw === 'object') {
    return disciplinesRaw;
  }

  return {};
};

const normalizeTopics = (topicsRaw) => {
  if (Array.isArray(topicsRaw)) {
    return topicsRaw.reduce((acc, topicItem) => {
      if (!topicItem || typeof topicItem !== 'object' || Array.isArray(topicItem)) {
        return acc;
      }

      Object.entries(topicItem).forEach(([topicName, topicData]) => {
        const subtopicsObj = topicData?.subtopics || {};
        acc[topicName] = {
          subtopics: subtopicsObj,
        };
      });

      return acc;
    }, {});
  }

  if (topicsRaw && typeof topicsRaw === 'object') {
    return topicsRaw;
  }

  return {};
};

const buildGraphDataFromProgram = (programJson) => {
  const [programName, disciplinesRaw] = Object.entries(programJson || {})[0] || [];
  if (!programName) {
    return {};
  }

  const disciplines = normalizeDisciplines(disciplinesRaw);
  const graphData = {};

  Object.entries(disciplines).forEach(([disciplineName, disciplineData]) => {
    const prev = Array.isArray(disciplineData?.previousDisciplines)
      ? disciplineData.previousDisciplines
      : [];

    const topicsObject = normalizeTopics(disciplineData?.topics);

    const topics = Object.keys(topicsObject);
    const topicsWithSubtopics = Object.entries(topicsObject).map(([topicName, topicData]) => {
      const subtopicsData = topicData?.subtopics;
      let subtopicsList = [];
      if (Array.isArray(subtopicsData)) {
        subtopicsList = subtopicsData;
      } else if (subtopicsData && typeof subtopicsData === 'object') {
        subtopicsList = Object.keys(subtopicsData);
      }
      return {
        name: topicName,
        subtopics: subtopicsList,
      };
    });

    graphData[disciplineName] = {
      предметы_до: prev,
      предметы_после: [],
      список_тем: topics,
      темы: topicsWithSubtopics,
    };
  });

  Object.keys(graphData).forEach((subjectName) => {
    const predecessors = graphData[subjectName].предметы_до;
    predecessors.forEach((pred) => {
      if (!graphData[pred]) {
        graphData[pred] = {
          предметы_до: [],
          предметы_после: [],
          список_тем: [],
        };
      }

      if (!graphData[pred].предметы_после.includes(subjectName)) {
        graphData[pred].предметы_после.push(subjectName);
      }
    });
  });

  return graphData;
};

export const fetchGraphData = async (userId, programFolder, universityName) => {
  const params = new URLSearchParams({
    pathToProgramFolder: programFolder,
  });

  if (universityName) {
    params.set('universityName', universityName);
  }

  const response = await fetchWithAuth(`${API_BASE_URL}/show-graph?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const rawData = await response.json();
  return buildGraphDataFromProgram(rawData);
};

export const fetchGraphBridges = async (userId, programFolder, universityName) => {
  const graphId = buildGraphId(userId, programFolder, universityName);
  return fetchGraphBridgesById(graphId);
};

export const fetchGraphBridgesById = async (graphId) => {
  const params = new URLSearchParams({ graphId });

  const response = await fetch(`${API_BASE_URL}/find-graph-bridges?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const rawData = await response.json();
  return Array.isArray(rawData?.bridges) ? rawData.bridges : [];
};