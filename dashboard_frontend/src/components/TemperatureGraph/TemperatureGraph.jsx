import React, { useEffect, useState } from 'react';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Label,
} from 'recharts';

import './TemperatureGraph.css';
import { getCharData } from '../../api/getCharData';
import { formatNumber } from '../../utils/tranform';

const TemperatureGraph = () => {
  const [data, setData] = useState([]);
  const [interval, setInterval] = useState(8);
  const [chartHeight, setChartHeight] = useState(600);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const findYAxisDomain = (data) => {
    if (!data || data.length === 0) return ['auto', 'auto'];

    const allTemps = data.reduce((temps, entry) => {
      temps.push(entry.inlet, entry.outlet);
      return temps;
    }, []);

    const min = Math.min(...allTemps);
    const max = Math.max(...allTemps);

    const padding = (max - min) * 0.05;
    return [Math.floor(min - padding), Math.ceil(max + padding)];
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await getCharData();
        const result = await response.data;

        if (!result || result.length === 0) {
          setError('No data available');
          return;
        }

        const mappedData = result.map((entry) => ({
          date: new Date(entry.date).toLocaleString('en-US', {
            timeZone: 'America/Chicago',
            year: 'numeric',
            month: 'numeric',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
          }),
          inlet: formatNumber(entry['column-2'], 1),
          outlet: formatNumber(entry['column-1'], 1),
        }));

        setData(mappedData);
      } catch (error) {
        setError('Failed to load data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
    const intervalId = setInterval(() => {
      if (data.length === 0 || error) {
        fetchData();
      }
    }, 10000);

    const updateIntervalId = setInterval(() => {
      if (data.length > 0) {
        fetchData();
      }
    }, 120000);

    const handleResize = () => {
      if (window.innerWidth < 768) {
        setInterval(16);
        setChartHeight(400);
      } else {
        setInterval(8);
        setChartHeight(600);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);

    return () => {
      clearInterval(intervalId);
      clearInterval(updateIntervalId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div
          className="custom-tooltip"
          style={{
            backgroundColor: '#333645',
            padding: '8px 12px',
            borderRadius: '5px',
            fontSize: '12px',
            maxWidth: '200px',
            color: '#fff',
          }}
        >
          <p style={{ fontSize: '12px', margin: '5px 0' }}>
            <strong>Time: </strong>
            {label}
          </p>
          <p style={{ fontSize: '12px', margin: '5px 0', color: '#ffca28' }}>
            <strong>Inlet: </strong>
            {payload[0].value}°F
          </p>
          <p style={{ fontSize: '12px', margin: '5px 0', color: '#ff7043' }}>
            <strong>Outlet: </strong>
            {payload[1].value}°F
          </p>
        </div>
      );
    }
    return null;
  };

  const downloadCSV = () => {
    const header = [
      'Date',
      'Inlet Temperature (°F)',
      'Outlet Temperature (°F)',
    ];
    const rows = data.map((entry) => [entry.date, entry.inlet, entry.outlet]);

    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += header.join(',') + '\n';

    rows.forEach((row) => {
      csvContent += row.join(',') + '\n';
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'temperature_data.csv');
    link.click();
  };

  return (
    <div className="graph-container">
      <div className="graphbody">
        <h3>Inlet/Outlet Temperature History</h3>
        {isLoading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading temperature data...</p>
          </div>
        )}
        {error && !isLoading && (
          <div className="error-state">
            <p>{error}</p>
          </div>
        )}
        <>
          {!isLoading && !error && data.length > 0 && (
            <>
              <ResponsiveContainer width="100%" height={chartHeight}>
                <LineChart data={data}>
                  <CartesianGrid stroke="#4c5c77" strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    stroke="#dddddd"
                    tick={{ fill: '#dddddd', fontSize: 12, fontWeight: 'bold' }}
                    tickFormatter={(tick) => {
                      const [, time] = tick.split(', ');
                      return time;
                    }}
                    angle={0}
                    textAnchor="left"
                    height={60}
                    interval={interval}
                  />
                  <YAxis
                    stroke="#dddddd"
                    tick={{ fill: '#dddddd', fontSize: 12, fontWeight: 'bold' }}
                    tickFormatter={(tick) => parseFloat(tick.toFixed(1))}
                    domain={findYAxisDomain(data)}
                    padding={{ top: 30, bottom: 30 }}
                  >
                    <Label
                      value="Temperature (°F)"
                      angle={-90}
                      position="insideLeft"
                      fill="#dddddd"
                      style={{ textAnchor: 'middle', fontSize: 18 }}
                    />
                  </YAxis>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend
                    verticalAlign="top"
                    align="right"
                    wrapperStyle={{ fill: '#dddddd' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="inlet"
                    stroke="#ffca28"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="outlet"
                    stroke="#ff7043"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                </LineChart>
              </ResponsiveContainer>
              <button
                className="download-button m-2"
                onClick={downloadCSV}
                disabled={isLoading || data.length === 0}
              >
                Download logs csv
              </button>
            </>
          )}
        </>
      </div>
    </div>
  );
};

export default TemperatureGraph;
