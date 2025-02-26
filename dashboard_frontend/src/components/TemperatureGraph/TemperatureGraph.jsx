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
import { formatNumber } from '../../utils/tranform';

const TemperatureGraph = ({ data }) => {
  const [chartData, setChartData] = useState([]);
  const [interval, setInterval] = useState(8);
  const [chartHeight, setChartHeight] = useState(600);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dataInterval, setDataInterval] = useState(1);

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

  const convertToUnixChicago = (dateStr) =>
    Math.floor(
      new Date(
        new Date(dateStr).toLocaleString('en-US', {
          timeZone: 'America/Chicago',
        }),
      ).getTime() / 1000,
    );

  useEffect(() => {
    if (data) {
      try {
        const mappedData = data.map((entry) => ({
          date: convertToUnixChicago(entry.date),
          inlet: formatNumber(entry['column-2'], 1),
          outlet: formatNumber(entry['column-1'], 1),
        }));
        setChartData(mappedData);
        setIsLoading(false);
        setError(null);
      } catch (error) {
        setError('Failed to process data');
        setIsLoading(false);
      }
    }
  }, [data]);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setInterval(8);
        setChartHeight(350);
        setDataInterval(4);
      } else if (window.innerWidth < 1024) {
        setInterval(8);
        setChartHeight(450);
        setDataInterval(1);
      } else {
        setInterval(8);
        setChartHeight(600);
        setDataInterval(1);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);

    return () => {
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
            fontSize: window.innerWidth < 768 ? '14px' : '12px',
            maxWidth: '200px',
            color: '#fff',
          }}
        >
          <p
            style={{
              fontSize: window.innerWidth < 768 ? '14px' : '12px',
              margin: '5px 0',
            }}
          >
            <strong>Time: </strong>
            {label}
          </p>
          <p
            style={{
              fontSize: window.innerWidth < 768 ? '14px' : '12px',
              margin: '5px 0',
              color: '#ffca28',
            }}
          >
            <strong>Inlet: </strong>
            {payload[0].value}°F
          </p>
          <p
            style={{
              fontSize: window.innerWidth < 768 ? '14px' : '12px',
              margin: '5px 0',
              color: '#ff7043',
            }}
          >
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
    const rows = chartData.map((entry) => [
      entry.date,
      entry.inlet,
      entry.outlet,
    ]);

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

  const getResponsiveFontSize = () => {
    return window.innerWidth < 768 ? 12 : 12;
  };

  const getFilteredData = (data) => {
    if (window.innerWidth < 768) {
      return data.filter((_, index) => index % dataInterval === 0);
    }
    return data;
  };

  return (
    <div className="graph-container p-0">
      <div className="graphbody">
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
        {!isLoading && !error && chartData.length > 0 && (
          <>
            <ResponsiveContainer width="100%" height={chartHeight}>
              <LineChart data={getFilteredData(chartData)}>
                <CartesianGrid stroke="#4c5c77" strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  stroke="#dddddd"
                  tick={{ fill: '#dddddd', fontSize: 12, fontWeight: 'bold' }}
                  angle={0}
                  textAnchor="middle"
                  height={60}
                  tickFormatter={(val) =>
                    new Date(val * 1000).toLocaleTimeString('en-US', {
                      timeZone: 'America/Chicago',
                      hour: '2-digit',
                      minute: '2-digit',
                      hour12: false,
                    })
                  }
                  interval="preserveStartEnd"
                  type="number"
                  domain={['dataMin', 'dataMax']}
                  allowDataOverflow
                  padding={{ left: 30, right: 30 }}
                  ticks={chartData
                    .map((d) => d.date)
                    .filter((timestamp) => {
                      const minutes = new Date(timestamp * 1000).getMinutes();
                      return minutes % 5 === 0;
                    })}
                />
                <YAxis
                  stroke="#dddddd"
                  tick={{ fill: '#dddddd', fontSize: 12, fontWeight: 'bold' }}
                  tickFormatter={(tick) => parseFloat(tick.toFixed(1))}
                  domain={findYAxisDomain(chartData)}
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
                  activeDot={{ r: 5 }}
                />
                <Line
                  type="monotone"
                  dataKey="outlet"
                  stroke="#ff7043"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
            <button
              className="download-button"
              onClick={downloadCSV}
              disabled={isLoading || chartData.length === 0}
            >
              Download logs csv
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default TemperatureGraph;
