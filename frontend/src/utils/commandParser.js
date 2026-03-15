export const parseCommand = (input) => {
  if (!input.startsWith('/')) return null;
  
  const parts = input.slice(1).split(' ');
  const command = parts[0].toLowerCase();
  const args = parts.slice(1);
  
  return { command, args };
};

export const getCommandHelp = () => {
  return [
    { command: '/help', description: 'Show all available commands' },
    { command: '/rooms', description: 'List all available rooms' },
    { command: '/kick @user', description: 'Remove a user (Mod+)' },
    { command: '/promote @user', description: 'Change user role (Admin only)' },
  ];
};
