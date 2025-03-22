from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un elemento de un diccionario por su clave"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def get_grid_answer(grid_answers, row, col=None):
    """Obtiene la respuesta de una celda de cuadrícula"""
    if grid_answers is None:
        return False
    
    # Si se pasan dos argumentos (row_col como string y col como None)
    if col is None and isinstance(row, str) and '_' in row:
        parts = row.split('_')
        if len(parts) >= 2:
            row, col = parts[0], parts[1]
    
    key = f"{row}_{col}"
    return key in grid_answers