import React from 'react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

// Mock para el enrutador
export const MockRouter = ({ children, initialEntries = ['/'] }) => {
  return (
    <MemoryRouter initialEntries={initialEntries}>
      {children}
    </MemoryRouter>
  );
};

// Mock para rutas completas
export const MockRoutes = ({ routes, initialPath = '/' }) => {
  return (
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        {routes.map((route) => (
          <Route
            key={route.path}
            path={route.path}
            element={route.element}
          />
        ))}
      </Routes>
    </MemoryRouter>
  );
};

// Función de ayuda para crear un wrapper con router
export const createRouterWrapper = (initialEntries = ['/', '/login', '/register']) => {
  return ({ children }) => (
    <MemoryRouter initialEntries={initialEntries}>
      {children}
    </MemoryRouter>
  );
};
