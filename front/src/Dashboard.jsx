import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, LineChart, Line, ResponsiveContainer
} from 'recharts';
import './Dashboard.css';

const COLORS = ['#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#0088FE'];

const Dashboard = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/metrics-data')
      .then(response => setData(response.data))
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  if (!data) {
    return <div className="loading">Cargando datos...</div>;
  }

  const comprasPorUsuario = Object.entries(data.purchase.user_counts).map(([_, count], index) => ({
    name: `Usuario ${index + 1}`,
    compras: count
  }));
  

  const loginsPorDispositivo = Object.entries(data.login.devices).map(([device, count]) => ({
    name: device,
    value: count
  }));

  const loginsPorPlataforma = Object.entries(data.login.platforms).map(([platform, count]) => ({
    name: platform,
    value: count
  }));

  const ratingsDistribucion = data.reviews.ratings.reduce((acc, val) => {
    acc[val] = (acc[val] || 0) + 1;
    return acc;
  }, {});

  const ratingsData = Object.entries(ratingsDistribucion).map(([rating, count]) => ({
    rating,
    count
  }));

  const comprasEnTiempo = data.purchase.timestamps.map((ts, i) => ({
    timestamp: ts,
    tiempo: data.purchase.elapsed_times[i]
  })).filter(d => d.timestamp);

  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">Dashboard de Métricas</h1>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Compras por Usuario</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={comprasPorUsuario}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2f3b" />
              <XAxis dataKey="name" stroke="#ccc" />
              <YAxis stroke="#ccc" />
              <Tooltip
                    cursor={false}
                    content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                        return (
                            <div style={{
                            backgroundColor: '#1e2a3d',
                            borderRadius: '12px',
                            padding: '10px 14px',
                            color: '#fff',
                            boxShadow: '0 0 10px rgba(0,0,0,0.3)',
                            fontFamily: 'Segoe UI, sans-serif',
                            }}>
                            <p style={{ margin: 0, fontSize: '0.9rem', color: '#bbb' }}>{payload[0].payload.name}</p>
                            <p style={{ margin: 0, fontSize: '1rem', fontWeight: 'bold', color: '#00C49F' }}>
                                Compras: {payload[0].value}
                            </p>
                            </div>
                        );
                        }
                        return null;
                    }}
                />

                <Bar dataKey="compras" fill="#00C49F" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="dashboard-card">
          <h3>Evolución de Tiempos de Compra</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={comprasEnTiempo}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2f3b" />
              <XAxis dataKey="timestamp" stroke="#ccc" tickFormatter={(tick) => tick.split("T")[0]} />
              <YAxis stroke="#ccc" />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const fecha = new Date(label);
                    const fechaFormateada = fecha.toLocaleDateString('es-ES', {
                      year: 'numeric',
                      month: '2-digit',
                      day: '2-digit'
                    });

                    return (
                      <div style={{
                        backgroundColor: '#1e2a3d',
                        borderRadius: '12px',
                        padding: '12px 16px',
                        color: '#fff',
                        boxShadow: '0 0 10px rgba(0,0,0,0.3)',
                        fontFamily: 'Segoe UI, sans-serif',
                      }}>
                        <p style={{ margin: 0, fontSize: '0.9rem', color: '#bbb' }}>{fechaFormateada}</p>
                        <p style={{ margin: 0, fontSize: '1rem', fontWeight: 'bold', color: '#FFBB28' }}>
                          Tiempo: {payload[0].value}
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Line type="monotone" dataKey="tiempo" stroke="#FFBB28" dot={{ r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="dashboard-card">
          <h3>Logins por Plataforma</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={loginsPorPlataforma} dataKey="value" nameKey="name" outerRadius={90} label>
                {loginsPorPlataforma.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div style={{
                        backgroundColor: '#1e2a3d',
                        borderRadius: '12px',
                        padding: '10px 14px',
                        color: '#fff',
                        fontFamily: 'Segoe UI, sans-serif'
                      }}>
                        <p style={{ margin: 0, fontSize: '0.95rem', fontWeight: 'bold' }}>
                          {payload[0].name}: {payload[0].value}
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="dashboard-card">
          <h3>Logins por Dispositivo</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={loginsPorDispositivo} dataKey="value" nameKey="name" outerRadius={90} label>
                {loginsPorDispositivo.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div style={{
                        backgroundColor: '#1e2a3d',
                        borderRadius: '12px',
                        padding: '10px 14px',
                        color: '#fff',
                        fontFamily: 'Segoe UI, sans-serif'
                      }}>
                        <p style={{ margin: 0, fontSize: '0.95rem', fontWeight: 'bold' }}>
                          {payload[0].name}: {payload[0].value}
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="dashboard-card full-width">
          <h3>Distribución de Calificaciones</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={ratingsData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2f3b" />
              <XAxis dataKey="rating" stroke="#ccc" />
              <YAxis stroke="#ccc" />
              <Tooltip
              cursor={false}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div style={{
                        backgroundColor: '#1e2a3d',
                        borderRadius: '12px',
                        padding: '10px 14px',
                        color: '#fff',
                        fontFamily: 'Segoe UI, sans-serif'
                      }}>
                        <p style={{ margin: 0, fontSize: '0.95rem', fontWeight: 'bold' }}>
                          Calificación: {payload[0].payload.rating}
                        </p>
                        <p style={{ margin: 0, fontSize: '0.9rem', color: '#8884d8' }}>
                          Veces: {payload[0].value}
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="count" fill="#8884d8" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
