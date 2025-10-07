import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { FiMail, FiLock, FiAlertCircle } from 'react-icons/fi'
import { toast } from 'react-toastify'

const LoginPage = () => {
  const { register, handleSubmit, formState: { errors } } = useForm()
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const onSubmit = async (data) => {
    try {
      setIsLoading(true)
      // Simulación de llamada a API - reemplazar con llamada real
      console.log('Login data:', data)
      
      // Simular delay de red
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Simulación de éxito
      toast.success('Inicio de sesión exitoso')
      navigate('/')
    } catch (error) {
      console.error('Error de inicio de sesión:', error)
      toast.error('Error al iniciar sesión. Verifique sus credenciales.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="bg-white shadow-md rounded-lg p-8">
        <h1 className="text-2xl font-bold text-center mb-6">Iniciar Sesión</h1>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Email Field */}
          <div>
            <label htmlFor="email" className="label">
              Correo Electrónico
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FiMail className="text-secondary-400" />
              </div>
              <input
                id="email"
                type="email"
                className={`input pl-10 w-full ${errors.email ? 'border-red-500' : ''}`}
                placeholder="correo@ejemplo.com"
                {...register("email", { 
                  required: "El correo electrónico es obligatorio",
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: "Ingrese un correo electrónico válido"
                  }
                })}
              />
            </div>
            {errors.email && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <FiAlertCircle className="mr-1" /> {errors.email.message}
              </p>
            )}
          </div>
          
          {/* Password Field */}
          <div>
            <label htmlFor="password" className="label">
              Contraseña
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FiLock className="text-secondary-400" />
              </div>
              <input
                id="password"
                type="password"
                className={`input pl-10 w-full ${errors.password ? 'border-red-500' : ''}`}
                placeholder="••••••••"
                {...register("password", { 
                  required: "La contraseña es obligatoria",
                  minLength: {
                    value: 8,
                    message: "La contraseña debe tener al menos 8 caracteres"
                  }
                })}
              />
            </div>
            {errors.password && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <FiAlertCircle className="mr-1" /> {errors.password.message}
              </p>
            )}
          </div>
          
          {/* Forgot Password Link */}
          <div className="text-right">
            <Link to="/recuperar-contrasena" className="text-sm text-primary-600 hover:text-primary-800">
              ¿Olvidaste tu contraseña?
            </Link>
          </div>
          
          {/* Submit Button */}
          <button
            type="submit"
            className="btn btn-primary w-full flex justify-center items-center"
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
            ) : (
              'Iniciar Sesión'
            )}
          </button>
        </form>
        
        {/* Register Link */}
        <div className="mt-6 text-center">
          <p className="text-secondary-600">
            ¿No tienes una cuenta?{' '}
            <Link to="/registro" className="text-primary-600 hover:text-primary-800 font-medium">
              Regístrate
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
