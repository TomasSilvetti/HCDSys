describe('Búsqueda de Documentos', () => {
  beforeEach(() => {
    // Cargar datos de usuario de prueba
    cy.fixture('users').then((users) => {
      const { usuario } = users;
      
      // Iniciar sesión usando el comando personalizado
      cy.login(usuario.email, usuario.password);
      
      // Visitar la página de búsqueda
      cy.visit('/search');
    });
  });

  it('Debe mostrar la interfaz de búsqueda', () => {
    // Verificar que se muestra la interfaz de búsqueda
    cy.contains('Búsqueda de Documentos').should('be.visible');
    cy.get('input[placeholder*="Buscar"]').should('be.visible');
    cy.contains('Filtros Avanzados').should('be.visible');
  });

  it('Debe realizar una búsqueda básica', () => {
    // Cargar términos de búsqueda
    cy.fixture('documents').then((documents) => {
      const { searchTerms } = documents;
      
      // Ingresar término de búsqueda
      cy.get('input[placeholder*="Buscar"]').type(searchTerms.valid);
      
      // Hacer clic en el botón de búsqueda
      cy.get('button').contains('Buscar').click();
      
      // Verificar que se muestran resultados
      cy.contains('Mostrando resultados').should('be.visible');
      
      // O si no hay resultados, verificar el mensaje correspondiente
      cy.get('body').then(($body) => {
        if ($body.text().includes('No se encontraron resultados')) {
          cy.contains('No se encontraron resultados').should('be.visible');
        } else {
          // Verificar que hay al menos un resultado
          cy.get('.bg-white.shadow').should('exist');
        }
      });
    });
  });

  it('Debe mostrar filtros avanzados', () => {
    // Hacer clic en el botón de filtros avanzados
    cy.contains('Filtros Avanzados').click();
    
    // Verificar que se muestran los filtros
    cy.contains('Tipo de Documento').should('be.visible');
    cy.contains('Fecha de Creación').should('be.visible');
    cy.contains('Creado por').should('be.visible');
    
    // Verificar que se pueden seleccionar filtros
    cy.get('input[type="checkbox"]').first().check();
    
    // Aplicar filtros
    cy.contains('Aplicar Filtros').click();
    
    // Verificar que se muestran los filtros activos
    cy.contains('Filtros Activos').should('be.visible');
  });

  it('Debe permitir limpiar los filtros', () => {
    // Hacer clic en el botón de filtros avanzados
    cy.contains('Filtros Avanzados').click();
    
    // Seleccionar un filtro
    cy.get('input[type="checkbox"]').first().check();
    
    // Aplicar filtros
    cy.contains('Aplicar Filtros').click();
    
    // Verificar que se muestran los filtros activos
    cy.contains('Filtros Activos').should('be.visible');
    
    // Limpiar filtros
    cy.contains('Limpiar Filtros').click();
    
    // Verificar que no hay filtros activos
    cy.contains('Filtros Activos').should('not.exist');
  });

  it('Debe mostrar mensaje cuando no hay resultados', () => {
    // Cargar términos de búsqueda
    cy.fixture('documents').then((documents) => {
      const { searchTerms } = documents;
      
      // Ingresar término de búsqueda que no dará resultados
      cy.get('input[placeholder*="Buscar"]').type(searchTerms.invalid);
      
      // Hacer clic en el botón de búsqueda
      cy.get('button').contains('Buscar').click();
      
      // Verificar que se muestra el mensaje de no resultados
      cy.contains('No se encontraron resultados').should('be.visible');
    });
  });
});
