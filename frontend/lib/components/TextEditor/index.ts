/**
 * Unhinged Platform Text Editor
 * =============================
 * 
 * Text editor component exports
 */

export { default as TextEditor } from './TextEditor';
export type { 
  TextEditorProps, 
  EditorInstance, 
  EditorLanguage, 
  EditorTheme, 
  EditorSize,
  EditorFeatures,
  EditorChangeEvent,
  EditorPosition,
  EditorRange
} from './types';
export { DEFAULT_FEATURES } from './types';
