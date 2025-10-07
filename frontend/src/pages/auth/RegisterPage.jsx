import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { FiUser, FiMail, FiLock, FiAlertCircle, FiCreditCard } from 'react-icons/fi'
import { toast } from 'react-toastify'

const RegisterPage = () => {
  const { register, handleSubmit, formState: { errors }, watch } = useForm()
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  
  const password = watch("password", "")

  const onSubmit = async (data) => {
    try {
      setIsLoading(true)
      // Simulación de llamada a API - reemplazar con llamada real
      console.log('Register data:', data)
      
      // Simular delay de red
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Simulación de éxito
      toast.success('Registro exitoso. Por favor inicia sesión.')
      navigate('/login')
    } catch (error) {
      console.error('Error de registro:', error)
      toast.error('Error al registrar usuario. Inténtelo nuevamente.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="bg-white shadow-md rounded-lg p-8">
        <h1 className="text-2xl font-bold text-center mb-6">Crear Cuenta</h1>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Full Name Field */}
          <div>
            <label htmlFor="fullName" className="label">
              Nombre y Apellido
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FiUser className="text-secondary-400" />
              </div>
              <input
                id="fullName"
                type="text"
                className={`input pl-10 w-full ${errors.fullName ? 'border-red-500' : ''}`}
                placeholder="Juan Pérez"
                {...register("fullName", { 
                  required: "El nombre y apellido son obligatorios",
                  minLength: {
                    value: 3,
                    message: "El nombre debe tener al menos 3 caracteres"
                  }
                })}
              />
            </div>
            {errors.fullName && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <FiAlertCircle className="mr-1" /> {errors.fullName.message}
              </p>
            )}
          </div>
          
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
          
          {/* DNI Field */}
          <div>
            <label htmlFor="dni" className="label">
              DNI
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FiCreditCard className="text-secondary-400" />
              </div>
              <input
                id="dni"
                type="text"
                className={`input pl-10 w-full ${errors.dni ? 'border-red-500' : ''}`}
                placeholder="12345678"
                {...register("dni", { 
                  required: "El DNI es obligatorio",
                  pattern: {
                    value: /^[0-9]{7,8}$/,
                    message: "Ingrese un DNI válido (7-8 dígitos)"
                  }
                })}
              />
            </div>
            {errors.dni && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <FiAlertCircle className="mr-1" /> {errors.dni.message}
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
                  },
                  pattern: {
                    value: /^(?=.*[A-Z]).{8,}$/,
                    message: "La contraseña debe tener al menos una mayúscula"
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
          
          {/* Confirm Password Field */}
          <div>
            <label htmlFor="confirmPassword" className="label">
              Confirmar Contraseña
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FiLock className="text-secondary-400" />
              </div>
              <input
                id="confirmPassword"
                type="password"
                className={`input pl-10 w-full ${errors.confirmPassword ? 'border-red-500' : ''}`}
                placeholder="••••••••"
                {...register("confirmPassword", { 
                  required: "Debe confirmar la contraseña",
                  validate: value => value === password || "Las contraseñas no coinciden"
                })}
              />
            </div>
            {errors.confirmPassword && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <FiAlertCircle className="mr-1" /> {errors.confirmPassword.message}
              </p>
            )}
          </div>
          
          {/* Submit Button */}
          <button
            type="submit"
            className="btn btn-primary w-full flex justify-center items-center mt-6"
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
            ) : (
              'Crear Cuenta'
            )}
          </button>
        </form>
        
        {/* Login Link */}
        <div className="mt-6 text-center">
          <p className="text-secondary-600">
            ¿Ya tienes una cuenta?{' '}
            <Link to="/login" className="text-primary-600 hover:text-primary-800 font-medium">
              Inicia Sesión
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
