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
const EditDocumentPage = lazy(() => import('./pages/documents/EditDocumentPage'))
const DocumentDetailPage = lazy(() => import('./pages/documents/DocumentDetailPage'))
const ProfilePage = lazy(() => import('./pages/user/ProfilePage'))
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
          
          {/* Página de perfil */}
          <Route path="perfil" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
          
          {/* Rutas protegidas para documentos */}
          <Route path="documentos">
            {/* Rutas para todos los usuarios autenticados */}
            <Route path=":id" element={<ProtectedRoute><DocumentDetailPage /></ProtectedRoute>} />
            
            {/* Rutas solo para gestores y administradores */}
            <Route path="cargar" element={<GestorRoute><UploadDocumentPage /></GestorRoute>} />
            <Route path=":id/editar" element={<GestorRoute><EditDocumentPage /></GestorRoute>} />
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
