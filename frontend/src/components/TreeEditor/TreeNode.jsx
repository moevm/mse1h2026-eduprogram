import React, { useState } from 'react';
import { getChildType, getRussianType, getPlaceholder, generateId } from './utils';
import './TreeEditor.css';

const TreeNode = ({ node, onUpdate, level = 0 }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const childType = getChildType(node.type);
  const canAddChild = childType !== null;

  const handleNameChange = (e) => {
    onUpdate({
      ...node,
      name: e.target.value
    });
  };

  const handleAddChild = () => {
    if (!childType) return;

    const newChild = {
      id: generateId(),
      name: '',
      type: childType,
      children: []
    };

    onUpdate({
      ...node,
      children: [...node.children, newChild]
    });
  };

  const handleChildUpdate = (childIndex, updatedChild) => {
    const newChildren = [...node.children];
    newChildren[childIndex] = updatedChild;
    onUpdate({
      ...node,
      children: newChildren
    });
  };

  const handleDelete = () => {
    if (window.confirm(`Удалить ${getRussianType(node.type)} "${node.name || 'без названия'}"?`)) {
      onUpdate(null);
    }
  };

  return (
    <div className="tree-node" style={{ marginLeft: level * 24 }}>
      <div className="node-content">
        <button
          className="toggle-btn"
          onClick={() => setIsExpanded(!isExpanded)}
          disabled={!node.children || node.children.length === 0}
        >
          {node.children && node.children.length > 0 
            ? (isExpanded ? '▼' : '►') 
            : '•'}
        </button>

        <input
          type="text"
          className="node-input"
          value={node.name}
          onChange={handleNameChange}
          placeholder={getPlaceholder(node.type)}
        />

        <span className="type-badge">{getRussianType(node.type)}</span>

        {canAddChild && (
          <button
            className="action-btn add-btn"
            onClick={handleAddChild}
            title={`Добавить ${childType}`}
          >
            ➕
          </button>
        )}

        <button
          className="action-btn delete-btn"
          onClick={handleDelete}
          title="Удалить"
        >
          🗑️
        </button>
      </div>

      {isExpanded && node.children && node.children.length > 0 && (
        <div className="children-container">
          {node.children.map((child, index) => (
            <TreeNode
              key={child.id}
              node={child}
              onUpdate={(updatedChild) => {
                if (updatedChild === null) {
                  const newChildren = node.children.filter((_, i) => i !== index);
                  onUpdate({
                    ...node,
                    children: newChildren
                  });
                } else {
                  handleChildUpdate(index, updatedChild);
                }
              }}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default TreeNode;