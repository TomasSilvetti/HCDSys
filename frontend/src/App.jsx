import { Routes, Route } from 'react-router-dom'
import { lazy, Suspense } from 'react'

// Layouts
import MainLayout from './components/layouts/MainLayout'
import AdminRoute from './components/auth/AdminRoute'
import ProtectedRoute from './components/auth/ProtectedRoute'
import GestorRoute from './components/auth/GestorRoute'
import AuthErrorNotification from './components/ui/AuthErrorNotification'

// Pages
const HomePage = lazy(() => import('./pages/HomePage'))
const LoginPage = lazy(() => import('./pages/auth/LoginPage'))
const RegisterPage = lazy(() => import('./pages/auth/RegisterPage'))
const SearchPage = lazy(() => import('./pages/search/SearchPage'))
const UploadDocumentPage = lazy(() => import('./pages/documents/UploadDocumentPage'))
const DocumentDetailPage = lazy(() => import('./pages/documents/DocumentDetailPage'))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'))
const AccessDeniedPage = lazy(() => import('./pages/AccessDeniedPage'))

// Admin Pages
const UserManagementPage = lazy(() => import('./pages/admin/UserManagementPage'))
const EditUserRolePage = lazy(() => import('./pages/admin/EditUserRolePage'))
const UserRoleHistoryPage = lazy(() => import('./pages/admin/UserRoleHistoryPage'))

// Componente de carga
const Loading = () => (
  <div className="flex justify-center items-center h-screen">
    <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-600"></div>
  </div>
)

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <AuthErrorNotification />
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="registro" element={<RegisterPage />} />
          <Route path="buscar" element={<SearchPage />} />
          
          {/* Página de acceso denegado */}
          <Route path="acceso-denegado" element={<AccessDeniedPage />} />
          
          {/* Rutas protegidas para usuarios autenticados */}
          <Route path="documentos" element={<ProtectedRoute />}>
            <Route path=":id" element={<DocumentDetailPage />} />
          </Route>
          
          {/* Rutas protegidas para gestores de documentos */}
          <Route path="documentos" element={<GestorRoute />}>
            <Route path="cargar" element={<UploadDocumentPage />} />
          </Route>
          
          {/* Rutas de administración protegidas */}
          <Route path="admin" element={<AdminRoute />}>
            <Route path="users" element={<UserManagementPage />} />
            <Route path="users/:userId/edit-role" element={<EditUserRolePage />} />
            <Route path="users/:userId/history" element={<UserRoleHistoryPage />} />
          </Route>
          
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </Suspense>
  )
}

export default App
