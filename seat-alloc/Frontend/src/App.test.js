import React from 'react';

// CRA + Jest in this project cannot resolve react-router-dom v7 in test runtime.
// Use a lightweight virtual mock so App can be imported for smoke testing.
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }) => <>{children}</>,
  MemoryRouter: ({ children }) => <>{children}</>,
  Routes: ({ children }) => <>{children}</>,
  Route: ({ element }) => element || null,
  Navigate: () => null,
  Outlet: () => null,
  Link: ({ children }) => <>{children}</>,
  NavLink: ({ children }) => <>{children}</>,
  useLocation: () => ({ pathname: '/' }),
  useNavigate: () => jest.fn(),
  useParams: () => ({}),
}), { virtual: true });

import App from './App';

test('exports App component', () => {
  expect(typeof App).toBe('function');
});
