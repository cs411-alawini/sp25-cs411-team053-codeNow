import React from 'react';

function Header() {
  return (
    <header style={styles.header}>
      <h1 style={styles.title}>CareerCompass</h1>
      <input
        type="text"
        placeholder="Search bar"
        style={styles.search}
      />
    </header>
  );
}

const styles = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px',
    borderBottom: '1px solid #ccc',
  },
  title: {
    fontSize: '28px',
  },
  search: {
    padding: '8px',
    fontSize: '16px',
  }
};

export default Header;
