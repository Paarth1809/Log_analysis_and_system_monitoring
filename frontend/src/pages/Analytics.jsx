import React from 'react';
import ChartsSection from '../components/ChartsSection';
import { useOutletContext } from 'react-router-dom';

const Analytics = () => {
    const { stats } = useOutletContext();
    return <ChartsSection stats={stats} />;
};

export default Analytics;
