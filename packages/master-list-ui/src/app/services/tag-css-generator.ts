import { Injectable } from '@angular/core';
import { ColorFactoryService } from './color-factory.service';
import { Activity, Project } from '../types/projtect';
// import { TagGroupOption } from '../types/tag/tag-group-option';
import { TagGroup, TagGroupOption, TagSelection, TagSelectionGroup } from '../types/tag';
// import { Activity, Project, TagGroup, TagGroupOption, TagLoad, TagSelection, TagSelectionGroup } from '@critical-pass/project/types';
// import { ColorFactoryService } from '@critical-pass/shared/serializers';

@Injectable({
    providedIn: 'root',
})
export class TagCssGenerator {
  // Add this to your component or create a separate service

  /**
   * A map of known tag names to their respective colors
   * You can populate this from your application settings or API
   */
  private tagColorMap: Map<string, string> = new Map();

  /**
   * Initialize the tag color map with some defaults
   * You would typically load these from configuration or user preferences
   */
  private initializeTagColors(): void {
    // Example predefined colors
    this.tagColorMap.set('important', '#e74c3c');
    this.tagColorMap.set('personal', '#3498db');
    this.tagColorMap.set('work', '#2ecc71');
    this.tagColorMap.set('urgent', '#f39c12');
    // You can add more default mappings as needed
  }

  /**
   * Ensures dynamic CSS for tags exists in the document
   * @param tags All unique tags that need CSS rules
   */
  public ensureTagStyles(tags: string[]): void {
    // Get or create the style element for our dynamic tag styles
    let styleElement = document.getElementById(
      'dynamic-tag-styles'
    ) as HTMLStyleElement;
  
    if (!styleElement) {
      // Create the style element if it doesn't exist
      styleElement = document.createElement('style');
      styleElement.id = 'dynamic-tag-styles';
      document.head.appendChild(styleElement);
    }
  
    // Create CSS rules for all tags
    let cssRules = '';
  
    // First, add a default rule for missing tags (white)
    cssRules += `.tag-default::before { background-color: white; }\n`;
  
    // Process each unique tag
    const uniqueTags = [...new Set(tags)];
    uniqueTags.forEach((tag) => {
      const sanitizedTag = this.sanitizeTagForCssClass(tag);
  
      // Get the color for this tag
      const color = this.getColorForTag(tag);
  
      // Add CSS rule for this tag targeting the ::before pseudo-element
      cssRules += `.tag-${sanitizedTag}::before { background-color: ${color}; }\n`;
    });
  
    // Set the CSS content
    styleElement.textContent = cssRules;
  }
//   public ensureTagStyles(tags: string[]): void {
//     // Get or create the style element for our dynamic tag styles
//     let styleElement = document.getElementById(
//       'dynamic-tag-styles'
//     ) as HTMLStyleElement;

//     if (!styleElement) {
//       // Create the style element if it doesn't exist
//       styleElement = document.createElement('style');
//       styleElement.id = 'dynamic-tag-styles';
//       document.head.appendChild(styleElement);
//     }

//     // Create CSS rules for all tags
//     let cssRules = '';

//     // First, add a default rule
//     cssRules += `.tag-default { --bullet-color: white; }\n`;

//     // Process each unique tag
//     const uniqueTags = [...new Set(tags)];
//     uniqueTags.forEach((tag) => {
//       const sanitizedTag = this.sanitizeTagForCssClass(tag);

//       // Get the color for this tag
//       let color = this.getColorForTag(tag);

//       // Add CSS rule for this tag
//       cssRules += `.tag-${sanitizedTag} { --bullet-color: ${color}; }\n`;
//     });

//     // Apply common style for all bullets to use the custom property
//     cssRules += `.bullet { background-color: var(--bullet-color, white); }\n`;

//     // Set the CSS content
//     styleElement.textContent = cssRules;
//   }

  /**
   * Gets a color for a specific tag, either from the map or generating one
   * @param tag The tag to get a color for
   * @returns A color string (hex, rgb, etc.)
   */
  private getColorForTag(tag: string): string {
    // Normalize the tag for lookup
    const normalizedTag = tag.toLowerCase().trim();

    // If we already have a color for this tag, return it
    if (this.tagColorMap.has(normalizedTag)) {
      return this.tagColorMap.get(normalizedTag)!;
    }

    // Otherwise, generate a color based on the tag string
    const color = this.generateColorFromString(normalizedTag);

    // Store it for future use
    this.tagColorMap.set(normalizedTag, color);

    return color;
  }

  /**
   * Generates a deterministic color from a string
   * @param str The input string
   * @returns A hex color code
   */
  private generateColorFromString(str: string): string {
    // Simple hash function
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }

    // Convert to hex color
    let color = '#';
    for (let i = 0; i < 3; i++) {
      const value = (hash >> (i * 8)) & 0xff;
      color += ('00' + value.toString(16)).substr(-2);
    }

    return color;
  }
  /**
   * Sanitizes a tag string to be used as part of a CSS class name
   * @param tag The original tag string
   * @returns A sanitized string suitable for use in a CSS class name
   */
  public sanitizeTagForCssClass(tag: string): string {
    // Remove special characters, convert to lowercase, replace spaces with hyphens
    return tag
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '-')
      .replace(/-+/g, '-') // Replace multiple hyphens with single hyphen
      .replace(/^-|-$/g, ''); // Remove leading/trailing hyphens
  }
}
