describe('Gestión de Documentos', () => {
  beforeEach(() => {
    // Cargar datos de usuario de prueba
    cy.fixture('users').then((users) => {
      const { gestor } = users;
      
      // Iniciar sesión como gestor
      cy.login(gestor.email, gestor.password);
    });
  });

  it('Debe permitir cargar un nuevo documento', () => {
    // Visitar la página de carga de documentos
    cy.visit('/documents/upload');
    
    // Verificar que se muestra el formulario de carga
    cy.contains('Cargar Documento').should('be.visible');
    
    // Cargar datos del documento
    cy.fixture('documents').then((documents) => {
      const { testDocument } = documents;
      
      // Completar el formulario
      cy.get('input[name="title"]').type(testDocument.title);
      cy.get('textarea[name="description"]').type(testDocument.description);
      cy.get('select[name="documentType"]').select(testDocument.documentType);
      
      // Adjuntar archivo
      cy.get('input[type="file"]').attachFile('sample.pdf');
      
      // Enviar el formulario
      cy.get('button[type="submit"]').click();
      
      // Verificar que se muestra un mensaje de éxito
      cy.contains('Documento cargado correctamente').should('be.visible');
      
      // Verificar que se redirige a la página de detalles del documento
      cy.url().should('include', '/documents/');
    });
  });

  it('Debe mostrar los detalles de un documento', () => {
    // Visitar la página de búsqueda
    cy.visit('/search');
    
    // Hacer clic en el primer documento de la lista
    cy.get('.bg-white.shadow').first().click();
    
    // Verificar que se muestra la página de detalles
    cy.url().should('include', '/documents/');
    cy.contains('Detalles del Documento').should('be.visible');
    
    // Verificar que se muestran los datos del documento
    cy.contains('Título:').should('be.visible');
    cy.contains('Descripción:').should('be.visible');
    cy.contains('Tipo de Documento:').should('be.visible');
    cy.contains('Fecha de Creación:').should('be.visible');
  });

  it('Debe permitir editar un documento', () => {
    // Visitar la página de búsqueda
    cy.visit('/search');
    
    // Hacer clic en el primer documento de la lista
    cy.get('.bg-white.shadow').first().click();
    
    // Verificar que se muestra la página de detalles
    cy.url().should('include', '/documents/');
    
    // Hacer clic en el botón de editar
    cy.contains('Editar').click();
    
    // Verificar que se muestra el formulario de edición
    cy.contains('Editar Documento').should('be.visible');
    
    // Cargar datos del documento actualizado
    cy.fixture('documents').then((documents) => {
      const { updatedDocument } = documents;
      
      // Actualizar el formulario
      cy.get('input[name="title"]').clear().type(updatedDocument.title);
      cy.get('textarea[name="description"]').clear().type(updatedDocument.description);
      
      // Enviar el formulario
      cy.get('button[type="submit"]').click();
      
      // Verificar que se muestra un mensaje de éxito
      cy.contains('Documento actualizado correctamente').should('be.visible');
      
      // Verificar que se redirige a la página de detalles del documento
      cy.url().should('include', '/documents/');
      
      // Verificar que los datos se actualizaron
      cy.contains(updatedDocument.title).should('be.visible');
      cy.contains(updatedDocument.description).should('be.visible');
    });
  });

  it('Debe mostrar el historial de versiones', () => {
    // Visitar la página de búsqueda
    cy.visit('/search');
    
    // Hacer clic en el primer documento de la lista
    cy.get('.bg-white.shadow').first().click();
    
    // Verificar que se muestra la página de detalles
    cy.url().should('include', '/documents/');
    
    // Verificar que se muestra el historial de versiones
    cy.contains('Historial de Versiones').should('be.visible');
    
    // Verificar que se muestra al menos una versión
    cy.contains('Versión').should('be.visible');
  });

  it('Debe permitir crear una nueva versión', () => {
    // Visitar la página de búsqueda
    cy.visit('/search');
    
    // Hacer clic en el primer documento de la lista
    cy.get('.bg-white.shadow').first().click();
    
    // Verificar que se muestra la página de detalles
    cy.url().should('include', '/documents/');
    
    // Hacer clic en el botón de nueva versión
    cy.contains('Nueva Versión').click();
    
    // Verificar que se muestra el formulario de nueva versión
    cy.contains('Crear Nueva Versión').should('be.visible');
    
    // Completar el formulario
    cy.get('textarea[name="comentario"]').type('Actualización de prueba');
    cy.get('textarea[name="cambios"]').type('Se actualizó el contenido del documento');
    
    // Adjuntar archivo
    cy.get('input[type="file"]').attachFile('sample.pdf');
    
    // Enviar el formulario
    cy.get('button[type="submit"]').click();
    
    // Verificar que se muestra un mensaje de éxito
    cy.contains('Versión creada correctamente').should('be.visible');
    
    // Verificar que se redirige a la página de detalles del documento
    cy.url().should('include', '/documents/');
    
    // Verificar que se muestra la nueva versión en el historial
    cy.contains('Actualización de prueba').should('be.visible');
  });
});
