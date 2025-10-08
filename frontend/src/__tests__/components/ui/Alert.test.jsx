import { render, screen } from '@testing-library/react';
import Alert from '../../../components/ui/Alert';

describe('Alert Component', () => {
  test('renders alert with correct message and type', () => {
    const message = 'Test alert message';
    const type = 'success';
    
    render(<Alert message={message} type={type} />);
    
    const alertElement = screen.getByText(message);
    expect(alertElement).toBeInTheDocument();
    expect(alertElement.parentElement).toHaveClass('bg-green-100'); // Asumiendo que success tiene bg-green-100
  });
  
  test('does not render when message is empty', () => {
    const { container } = render(<Alert message="" type="error" />);
    expect(container.firstChild).toBeNull();
  });
});
