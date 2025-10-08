// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// Comando para iniciar sesión
Cypress.Commands.add('login', (email, password) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/auth/login`,
    body: {
      email,
      password
    }
  }).then((response) => {
    expect(response.status).to.eq(200);
    expect(response.body).to.have.property('access_token');
    
    // Guardar el token en localStorage
    localStorage.setItem('authToken', response.body.access_token);
    localStorage.setItem('user', JSON.stringify(response.body.user));
    
    // También guardar en Cypress.env para uso posterior
    Cypress.env('authToken', response.body.access_token);
  });
});

// Comando para registrar un nuevo usuario
Cypress.Commands.add('register', (email, password, fullName) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/auth/register`,
    body: {
      email,
      password,
      full_name: fullName
    }
  }).then((response) => {
    expect(response.status).to.eq(201);
    expect(response.body).to.have.property('id');
  });
});

// Comando para cerrar sesión
Cypress.Commands.add('logout', () => {
  localStorage.removeItem('authToken');
  localStorage.removeItem('user');
  Cypress.env('authToken', null);
});

// Comando para crear un documento
Cypress.Commands.add('createDocument', (title, description, documentType, filePath) => {
  const token = Cypress.env('authToken');
  
  if (!token) {
    throw new Error('No hay token de autenticación disponible. Inicie sesión primero.');
  }
  
  // Crear un FormData
  const formData = new FormData();
  formData.append('title', title);
  formData.append('description', description);
  formData.append('document_type', documentType);
  
  // Adjuntar archivo si se proporciona
  if (filePath) {
    cy.fixture(filePath, 'binary').then((fileContent) => {
      const blob = Cypress.Blob.binaryStringToBlob(fileContent, 'application/pdf');
      formData.append('file', blob, filePath.split('/').pop());
      
      cy.request({
        method: 'POST',
        url: `${Cypress.env('apiUrl')}/documents/`,
        body: formData,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      }).then((response) => {
        expect(response.status).to.eq(201);
        expect(response.body).to.have.property('id');
      });
    });
  } else {
    cy.request({
      method: 'POST',
      url: `${Cypress.env('apiUrl')}/documents/`,
      body: formData,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body).to.have.property('id');
    });
  }
});
