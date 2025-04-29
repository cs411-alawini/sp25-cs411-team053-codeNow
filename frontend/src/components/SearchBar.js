import React, { useState } from 'react';
import axios from 'axios';

const SearchBar = ({ setSearchResults }) => {
  const [keyword, setKeyword] = useState('');

  const handleSearch = async () => {
    if (!keyword.trim()) return;

    try {
      const response = await axios.get(`/api/search_jobs/?keyword=${encodeURIComponent(keyword)}`);
      console.log('Search results:', response.data);
      setSearchResults(response.data);
    } catch (error) {
      console.error('Error during search:', error);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div style={{ marginBottom: '20px' }}>
      <input
        type="text"
        placeholder="Search careers..."
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        onKeyPress={handleKeyPress}
        style={{ marginRight: '10px' }}
      />
      <button onClick={handleSearch}>Search</button>
    </div>
  );
};

export default SearchBar;
