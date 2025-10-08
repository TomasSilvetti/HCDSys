describe('Autenticación', () => {
  beforeEach(() => {
    // Visitar la página de inicio antes de cada prueba
    cy.visit('/');
  });

  it('Debe mostrar la página de inicio sin autenticación', () => {
    // Verificar que se muestra la página de inicio
    cy.contains('Sistema de Gestión de Documentos').should('be.visible');
    cy.contains('Iniciar Sesión').should('be.visible');
    cy.contains('Registrarse').should('be.visible');
  });

  it('Debe permitir a un usuario registrarse', () => {
    // Cargar datos de usuario de prueba
    cy.fixture('users').then((users) => {
      const { newUser } = users;

      // Hacer clic en el botón de registro
      cy.contains('Registrarse').click();

      // Verificar que se muestra el formulario de registro
      cy.url().should('include', '/register');
      cy.contains('Crear una cuenta').should('be.visible');

      // Completar el formulario de registro
      cy.get('input[name="email"]').type(newUser.email);
      cy.get('input[name="password"]').type(newUser.password);
      cy.get('input[name="fullName"]').type(newUser.fullName);

      // Enviar el formulario
      cy.get('button[type="submit"]').click();

      // Verificar que se redirige a la página de inicio de sesión
      cy.url().should('include', '/login');
      cy.contains('Iniciar Sesión').should('be.visible');
    });
  });

  it('Debe permitir a un usuario iniciar sesión', () => {
    // Cargar datos de usuario de prueba
    cy.fixture('users').then((users) => {
      const { usuario } = users;

      // Hacer clic en el botón de inicio de sesión
      cy.contains('Iniciar Sesión').click();

      // Verificar que se muestra el formulario de inicio de sesión
      cy.url().should('include', '/login');
      cy.contains('Iniciar Sesión').should('be.visible');

      // Completar el formulario de inicio de sesión
      cy.get('input[name="email"]').type(usuario.email);
      cy.get('input[name="password"]').type(usuario.password);

      // Enviar el formulario
      cy.get('button[type="submit"]').click();

      // Verificar que se redirige a la página principal
      cy.url().should('include', '/search');
      cy.contains('Cerrar Sesión').should('be.visible');
    });
  });

  it('Debe mostrar un error con credenciales inválidas', () => {
    // Hacer clic en el botón de inicio de sesión
    cy.contains('Iniciar Sesión').click();

    // Completar el formulario con credenciales inválidas
    cy.get('input[name="email"]').type('invalid@example.com');
    cy.get('input[name="password"]').type('invalidpassword');

    // Enviar el formulario
    cy.get('button[type="submit"]').click();

    // Verificar que se muestra un mensaje de error
    cy.contains('Credenciales inválidas').should('be.visible');
  });

  it('Debe permitir a un usuario cerrar sesión', () => {
    // Cargar datos de usuario de prueba
    cy.fixture('users').then((users) => {
      const { usuario } = users;

      // Iniciar sesión usando el comando personalizado
      cy.login(usuario.email, usuario.password);

      // Visitar la página principal
      cy.visit('/search');

      // Verificar que el usuario está autenticado
      cy.contains('Cerrar Sesión').should('be.visible');

      // Hacer clic en el botón de cerrar sesión
      cy.contains('Cerrar Sesión').click();

      // Verificar que se redirige a la página de inicio
      cy.url().should('include', '/');
      cy.contains('Iniciar Sesión').should('be.visible');
    });
  });
});
