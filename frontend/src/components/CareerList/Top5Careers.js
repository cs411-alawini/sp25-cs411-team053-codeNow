import React from 'react';

function Top5Careers({ skills }) {
  const top5 = skills.slice(0, 5); // just for now, using 5

  return (
    <div>
      <h2>Top 5 Career Outlooks</h2>
      <ul>
        {top5.map(skill => (
          <li key={skill.id}>{skill.name}</li>
        ))}
      </ul>
    </div>
  );
}

export default Top5Careers;
