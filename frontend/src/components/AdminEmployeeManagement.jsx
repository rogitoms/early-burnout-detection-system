// frontend/src/components/AdminEmployeeManagement.jsx
import React, { useState, useEffect } from 'react';

const AdminEmployeeManagement = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);

  // Form states
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    is_active: true,
  });

  // ---- helpers ----
  const pickList = (data) => {
    if (Array.isArray(data)) return data;
    if (!data || typeof data !== 'object') return [];
    if (Array.isArray(data.employees)) return data.employees;
    if (Array.isArray(data.results)) return data.results;
    if (Array.isArray(data.users)) return data.users;
    if (Array.isArray(data.data)) return data.data;
    return [];
  };

  const normalizeEmployee = (e) => {
    const user = e.user || {};
    return {
      id: e.id ?? user.id ?? e.pk ?? e.uuid ?? Math.random().toString(36).slice(2),
      email: e.email ?? user.email ?? e.username ?? '-',
      employee_id:
        e.employee_id ??
        user.employee_id ??
        e.emp_id ??
        e.employeeNumber ??
        e.employee_no ??
        e.id ??
        '-',
      is_2fa_enabled:
        e.is_2fa_enabled ?? e.two_factor_enabled ?? e.has_2fa ?? user.is_2fa_enabled ?? false,
      is_active: e.is_active ?? user.is_active ?? true,
    };
  };

  // Fetch employees on component mount
  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/api/auth/admin/employees/', {
        method: 'GET',
        credentials: 'include',
      });
      const raw = await response.json().catch(() => ({}));
      if (!response.ok) {
        setError(raw?.message || `Failed to fetch employees (HTTP ${response.status})`);
      } else {
        const list = pickList(raw).map(normalizeEmployee);
        setEmployees(list);
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEmployee = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/api/auth/admin/employees/create/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await response.json().catch(() => ({}));
      if (response.ok) {
        setSuccess(data.message || 'Employee created.');
        setShowCreateModal(false);
        setFormData({ email: '', password: '', is_active: true });
        fetchEmployees();
      } else {
        setError(data.message || 'Failed to create employee');
      }
    } catch {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateEmployee = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const payload = { email: formData.email, is_active: formData.is_active };
      if (formData.password?.trim()) payload.password = formData.password.trim();

      const response = await fetch(
        `http://localhost:8000/api/auth/admin/employees/${editingEmployee.id}/update/`,
        {
          method: 'PUT',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        }
      );
      const data = await response.json().catch(() => ({}));
      if (response.ok) {
        setSuccess(data.message || 'Employee updated.');
        setShowEditModal(false);
        setEditingEmployee(null);
        setFormData({ email: '', password: '', is_active: true });
        fetchEmployees();
      } else {
        setError(data.message || 'Failed to update employee');
      }
    } catch {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteEmployee = async (employeeId, employeeEmail) => {
    if (!window.confirm(`Delete ${employeeEmail}? This cannot be undone.`)) return;
    setLoading(true);
    setError('');
    try {
      const response = await fetch(
        `http://localhost:8000/api/auth/admin/employees/${employeeId}/delete/`,
        { method: 'DELETE', credentials: 'include' }
      );
      let data = {};
      try { data = await response.json(); } catch {}
      if (response.ok) {
        setSuccess(data.message || 'Employee deleted.');
        fetchEmployees();
      } else {
        setError(data.message || 'Failed to delete employee');
      }
    } catch {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const openCreateModal = () => {
    setFormData({ email: '', password: '', is_active: true });
    setShowCreateModal(true);
    setError('');
    setSuccess('');
  };

  const openEditModal = (employee) => {
    setFormData({
      email: employee.email || '',
      password: '',
      is_active: !!employee.is_active,
    });
    setEditingEmployee(employee);
    setShowEditModal(true);
    setError('');
    setSuccess('');
  };

  const closeModals = () => {
    setShowCreateModal(false);
    setShowEditModal(false);
    setEditingEmployee(null);
    setError('');
    setSuccess('');
  };

  useEffect(() => {
    if (success || error) {
      const t = setTimeout(() => { setSuccess(''); setError(''); }, 5000);
      return () => clearTimeout(t);
    }
  }, [success, error]);

  return (
    <div className="admin-employee-management">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h3>Employee Management</h3>
        <button
          onClick={openCreateModal}
          style={{ backgroundColor: '#28a745', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: 5, cursor: 'pointer', fontSize: 14, fontWeight: 'bold' }}
        >
          + Add Employee
        </button>
      </div>

      {success && (
        <div style={{ padding: 10, backgroundColor: '#d4edda', color: '#155724', border: '1px solid #c3e6cb', borderRadius: 5, marginBottom: 20 }}>
          {success}
        </div>
      )}
      {error && (
        <div style={{ padding: 10, backgroundColor: '#f8d7da', color: '#721c24', border: '1px solid #f5c6cb', borderRadius: 5, marginBottom: 20 }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: 40 }}>Loading employees...</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: '#fff', border: '1px solid #ddd', borderRadius: 8, overflow: 'hidden' }}>
            <thead>
              <tr style={{ backgroundColor: '#f8f9fa', color: '#374151'}}>
                {/*<th style={{ padding: 12, textAlign: 'left', borderBottom: '2px solid #dee2e6', fontWeight: 'bold' }}>Employee ID</th>*/}
                <th style={{ padding: 12, textAlign: 'left', borderBottom: '2px solid #dee2e6', fontWeight: 'bold' }}>Email</th>
                <th style={{ padding: 12, textAlign: 'left', borderBottom: '2px solid #dee2e6', fontWeight: 'bold' }}>2FA Status</th>
                <th style={{ padding: 12, textAlign: 'left', borderBottom: '2px solid #dee2e6', fontWeight: 'bold' }}>Account Status</th>
                <th style={{ padding: 12, textAlign: 'center', borderBottom: '2px solid #dee2e6', fontWeight: 'bold' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ padding: 40, textAlign: 'center', color: '#666' }}>
                    No employees found. Click "Add Employee" to create one.
                  </td>
                </tr>
              ) : (
                employees.map((employee) => (
                  <tr key={employee.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                    {/*<td style={{ padding: 12, color:  '#374151', fontWeight: '600' }}>{employee.employee_id ?? '-'}</td>*/}
                    <td style={{ padding: 12, fontWeight: 500, color: '#374151' }}>{employee.email ?? '-'}</td>
                    <td style={{ padding: 12 }}>
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: 12,
                        fontSize: 12,
                        fontWeight: 'bold',
                        backgroundColor: employee.is_2fa_enabled ? '#d4edda' : '#f8d7da',
                        color: employee.is_2fa_enabled ? '#155724' : '#721c24'
                      }}>
                        {employee.is_2fa_enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </td>
                    <td style={{ padding: 12 }}>
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: 12,
                        fontSize: 12,
                        fontWeight: 'bold',
                        backgroundColor: employee.is_active ? '#d4edda' : '#f8d7da',
                        color: employee.is_active ? '#155724' : '#721c24'
                      }}>
                        {employee.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ padding: 12, textAlign: 'center' }}>
                      <button
                        onClick={() => openEditModal(employee)}
                        style={{ backgroundColor: '#007bff', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: 3, cursor: 'pointer', fontSize: 12, marginRight: 5 }}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteEmployee(employee.id, employee.email)}
                        style={{ backgroundColor: '#dc3545', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: 3, cursor: 'pointer', fontSize: 12 }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ backgroundColor: '#fff', padding: 30, borderRadius: 8, width: 400, maxWidth: '90vw', maxHeight: '90vh', overflowY: 'auto' }}>
            <h3>Create New Employee</h3>
            <form onSubmit={handleCreateEmployee}>
              <div style={{ marginBottom: 15 }}>
                <label style={{ display: 'block', marginBottom: 5, fontWeight: 'bold', color: '#333' }}>Email *</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  placeholder="employee@company.com"
                  style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ marginBottom: 20 }}>
                <label style={{ display: 'block', marginBottom: 5, fontWeight: 'bold', color: '#333' }}>Password *</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                  placeholder="Create a strong password"
                  style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ marginBottom: 20 }}>
                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    style={{ marginRight: 8, width: 16, height: 16 }}
                  />
                  <span style={{ fontWeight: 'bold', color: '#333' }}>Active Account</span>
                </label>
              </div>

              <div style={{ display: 'flex', gap: 10 }}>
                <button type="submit" disabled={loading} style={{ backgroundColor: '#28a745', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: 4, cursor: loading ? 'not-allowed' : 'pointer', fontSize: 14, flex: 1 }}>
                  {loading ? 'Creating...' : 'Create Employee'}
                </button>
                <button type="button" onClick={closeModals} style={{ backgroundColor: '#6c757d', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: 4, cursor: 'pointer', fontSize: 14, flex: 1 }}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingEmployee && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ backgroundColor: '#fff', padding: 30, borderRadius: 8, width: 400, maxWidth: '90vw', maxHeight: '90vh', overflowY: 'auto' }}>
            <h3>Edit Employee: {editingEmployee.email}</h3>
            <form onSubmit={handleUpdateEmployee}>
              <div style={{ marginBottom: 15 }}>
                <label style={{ display: 'block', marginBottom: 5, fontWeight: 'bold', color: '#333' }}>Email *</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  placeholder="employee@company.com"
                  style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ marginBottom: 15 }}>
                <label style={{ display: 'block', marginBottom: 5, fontWeight: 'bold', color: '#333' }}>
                  New Password (leave blank to keep current)
                </label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="Leave blank to keep current password"
                  style={{ width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ marginBottom: 20 }}>
                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    style={{ marginRight: 8, width: 16, height: 16 }}
                  />
                  <span style={{ fontWeight: 'bold', color: '#333' }}>Active Account</span>
                </label>
              </div>

              <div style={{ display: 'flex', gap: 10 }}>
                <button type="submit" disabled={loading} style={{ backgroundColor: '#007bff', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: 4, cursor: loading ? 'not-allowed' : 'pointer', fontSize: 14, flex: 1 }}>
                  {loading ? 'Updating...' : 'Update Employee'}
                </button>
                <button type="button" onClick={closeModals} style={{ backgroundColor: '#6c757d', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: 4, cursor: 'pointer', fontSize: 14, flex: 1 }}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminEmployeeManagement;
