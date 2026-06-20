const BASE = '/api';

async function request(path, options = {}) {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  return resp.json();
}

export const api = {
  health: () => request('/health'),

  getPolynomialLibrary: () => request('/polynomial/library'),
  generatePolynomial: (requirement) =>
    request('/polynomial/generate', {
      method: 'POST',
      body: JSON.stringify({ requirement }),
    }),
  computeSturm: (body) =>
    request('/polynomial/sturm', { method: 'POST', body: JSON.stringify(body) }),

  getSquareMatrices: () => request('/matrix/library/square'),
  getRectangularMatrices: () => request('/matrix/library/rectangular'),
  generateMatrix: (requirement, matrix_type = 'auto') =>
    request('/matrix/generate', {
      method: 'POST',
      body: JSON.stringify({ requirement, matrix_type }),
    }),
  computeMatrixProperties: (body) =>
    request('/matrix/properties', { method: 'POST', body: JSON.stringify(body) }),
  computeFullRank: (body) =>
    request('/matrix/decomposition/full-rank', { method: 'POST', body: JSON.stringify(body) }),
  computeLU: (body) =>
    request('/matrix/decomposition/lu', { method: 'POST', body: JSON.stringify(body) }),
  computeLDU: (body) =>
    request('/matrix/decomposition/ldu', { method: 'POST', body: JSON.stringify(body) }),
  computeSVD: (body) =>
    request('/matrix/decomposition/svd', { method: 'POST', body: JSON.stringify(body) }),
  computeJordan: (body) =>
    request('/matrix/jordan', { method: 'POST', body: JSON.stringify(body) }),
  computeLambdaSmith: (body) =>
    request('/matrix/lambda-smith', { method: 'POST', body: JSON.stringify(body) }),
};
