import requests
from PIL import Image
from io import BytesIO
import time
# URL of the logo
logo_url = "https://wsrv.nl/?w=128&h=128&default=1&url=https%3A%2F%2Fraw.githubusercontent.com%2Fsolana-labs%2Ftoken-list%2Fmain%2Fassets%2Fmainnet%2FSo11111111111111111111111111111111111111112%2Flogo.png"  # Replace with the actual URL

base_image_path = "top.png"  # Your existing PNG file
output_image_path = "output_image.png"  # Output file path
from PIL import Image, ImageDraw, ImageFont
import requests
import time
from io import BytesIO

def draw(fetched):
    timeNowInUnix = int(time.time())
    base_image_path = f"top.png"  # Your existing PNG file 
    output_image_path = f"output_image_{timeNowInUnix}.png"  # Output file path 
    
    if fetched:
        token_info = fetched[0]
        logo_url = token_info['logoUrl']
        name = token_info['name']
        symbol = token_info['symbol']
        
        try:
            # Fetch the logo from the URL 
            response = requests.get(logo_url) 
            response.raise_for_status()  # Raise an exception for bad status codes 
            
            # Open the logo as an image 
            logo_data = BytesIO(response.content) 
            logo = Image.open(logo_data) 
            base_image = Image.open(base_image_path) 
            
            # Create a draw object
            draw = ImageDraw.Draw(base_image)
            
            # Load a font (you may need to specify the path to a .ttf font file)
            try:
                # Try to use a system font
                font_name = ImageFont.truetype("arial.ttf", 36)
                font_symbol = ImageFont.truetype("arial.ttf", 24)
                font_price = ImageFont.truetype("arial.ttf", 24)
            except IOError:
                # Fallback to default font if specific font is not found
                font_name = ImageFont.load_default()
                font_symbol = ImageFont.load_default()
                font_price = ImageFont.load_default()
            
            # Write token name
            draw.text((50, 700), f"Name: {name}", fill=(255,255,255), font=font_name)
            
            # Write token symbol
            draw.text((50, 750), f"Symbol: {symbol.upper()}", fill=(255,255,255), font=font_symbol)
            
            # Write token price (formatted to 8 decimal places
            
            # Resize the logo if needed 
            logo_size = (80, 80)  # Desired logo size (width, height) 
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS)  # ANTIALIAS is deprecated, use LANCZOS instead 
 
            # Determine the position to place the logo (bottom-right corner) 
            base_width, base_height = base_image.size 
            logo_width, logo_height = logo.size 
            position = (470, 820)  # Padding of 10px 
 
            # Convert logo to RGBA if it isn't already 
            if logo.mode != "RGBA": 
                logo = logo.convert("RGBA") 
 
            # Paste the logo onto the base image using alpha channel 
            base_image.paste(logo, position, logo) 
 
            # Save the resulting image 
            base_image.save(output_image_path) 
            print(f"Image saved to {output_image_path}") 
 
        except requests.RequestException as e: 
            print(f"Failed to fetch the logo: {str(e)}") 
        except (IOError, OSError) as e: 
            print(f"Error processing image: {str(e)}") 
        except Exception as e: 
            print(f"An unexpected error occurred: {str(e)}")
        """{'wallet': 'Fj7WXfswWhFgeiSrHzpFVjzbchwnqMxowvQBX5f9qUra', 'amount': 895045338.229479,
          'shareInPercent': 89.505, 'netWorth': 7730.0, 'netWorthExcluding': 744.7229156896447,
            'firstTopHolding': {'address': '7FhLDYhLagEYx8mvheyWMo25ChQcM9F54TiM15Ydpump',
              'decimals': 6, 'balance': 895045338229479, 'uiAmount': 895045338.229479,
                'chainId': 'solana', 'name': 'spider cat', 'symbol': 'scat',
                  'icon': 'https://wsrv.nl/?w=128&h=128&default=1&url=https%3A%2F%2Fipfs.io%2Fipfs%2FQmes6UqktVkh2j8nSyDiW8nLns7Kg1UTmhy7tMnz3D9ukb',
                    'logoURI': 'https://wsrv.nl/?w=128&h=128&default=1&url=https%3A%2F%2Fipfs.io%2Fipfs%2FQmes6UqktVkh2j8nSyDiW8nLns7Kg1UTmhy7tMnz3D9ukb',
                      'priceUsd': 7.80438351662518e-06, 'valueUsd': 6985.277084310355},
                        'secondTopHolding': {'address': 'So11111111111111111111111111111111111111111', 'decimals': 9,
                          'balance': 3253808371, 'uiAmount': 3.253808371, 'chainId': 'solana', 'name': 'SOL',
                            'symbol': 'SOL',
                              'logoURI': 'https://wsrv.nl/?w=128&h=128&default=1&url=https%3A%2F%2Fraw.githubusercontent.com%2Fsolana-labs%2Ftoken-list%2Fmain%2Fassets%2Fmainnet%2FSo11111111111111111111111111111111111111112%2Flogo.png',
          'priceUsd': 228.93013011055416, 'valueUsd': 744.8947737278403}, 'thirdTopHolding': None}}"""
        # wallet = fetched['wallet']
        # amount = fetched['amount']
        # share_in_percent = fetched['shareInPercent']
        # net_worth = fetched['netWorth']
        # net_worth_excluding = fetched['netWorthExcluding']
        # first_top_holding = fetched['firstTopHolding']
        # second_top_holding = fetched['secondTopHolding']
        # third_top_holding = fetched['thirdTopHolding']
        # first_top_holding_logo = first_top_holding['logoURI']
        # first_top_holding_name = first_top_holding['name']
        # first_top_holding_symbol = first_top_holding['symbol']
        # second_top_holding_logo = second_top_holding['logoURI']
        # second_top_holding_name = second_top_holding['name']
        # second_top_holding_symbol = second_top_holding['symbol']
        # third_top_holding_logo = third_top_holding['logoURI']
        # third_top_holding_name = third_top_holding['name']
        # third_top_holding_symbol = third_top_holding['symbol']
        # print(first_top_holding_logo)
        # print(second_top_holding_logo)
        # print(third_top_holding_logo)
        # print(first_top_holding_name)
        # print(second_top_holding_name)
        # print(third_top_holding_name)
        # print(first_top_holding_symbol)
        # print(second_top_holding_symbol)
        # print(third_top_holding_symbol)
        
        
def draw_trials(par1, par2, par3):
    # Import required modules
    import time
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFont
    import requests

    timeNowInUnix = int(time.time())
    base_image_path = f"top.png"  # Your existing PNG file 
    output_image_path = f"output_image_{timeNowInUnix}.png"  # Output file path 
   
    logo_url = par1
    name = par2
    symbol = par3
    try:
        # Fetch the logo from the URL 
        response = requests.get(logo_url) 
        response.raise_for_status()  # Raise an exception for bad status codes 
            
        # Open the logo as an image 
        logo_data = BytesIO(response.content) 
        logo = Image.open(logo_data) 
        
        # Ensure base image exists before opening
        try:
            base_image = Image.open(base_image_path) 
        except FileNotFoundError:
            print(f"Base image not found at {base_image_path}")
            return
            
        # Create a draw object
        draw = ImageDraw.Draw(base_image)
            
        # Load a font (you may need to specify the path to a .ttf font file)
        try:
            # Try to use a system font
            font_name = ImageFont.truetype("arial.ttf", 36)
            font_symbol = ImageFont.truetype("arial.ttf", 24)
            font_price = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            # Fallback to default font if specific font is not found
            font_name = ImageFont.load_default()
            font_symbol = ImageFont.load_default()
            font_price = ImageFont.load_default()
          
        # Write token name
        draw.text((50, 700), f"Name: {name}", fill=(255,255,255), font=font_name)
          
        # Write token symbol  
        draw.text((50, 750), f"Symbol: {symbol.upper()}", fill=(255,255,255), font=font_symbol)
          
        # Resize the logo if needed 
        logo_size = (80, 80)  # Desired logo size (width, height) 
        logo = logo.resize(logo_size, Image.Resampling.LANCZOS)  # ANTIALIAS is deprecated, use LANCZOS instead 

        # Determine the position to place the logo (bottom-right corner) 
        base_width, base_height = base_image.size 
        logo_width, logo_height = logo.size 
        position = (470, 820)  # Padding of 10px 

        # Convert logo to RGBA if it isn't already 
        if logo.mode != "RGBA": 
            logo = logo.convert("RGBA") 

        # Paste the logo onto the base image using alpha channel 
        base_image.paste(logo, position, logo) 

        # Save the resulting image with absolute path
        import os
        output_path = os.path.abspath(output_image_path)
        base_image.show()
        # base_image.save(output_path, "PNG") 
        # print(f"Image saved to {output_path}")
        # return output_path

    except requests.RequestException as e: 
        print(f"Failed to fetch the logo: {str(e)}") 
    except (IOError, OSError) as e: 
        print(f"Error processing image: {str(e)}") 
    except Exception as e: 
        print(f"An unexpected error occurred: {str(e)}")
    # outputImage = Image.open(output_image_path)
    # outputImage.show()
    # return output_image_path
    
  
        
def shorten_address(address: str) -> str:
    """
    Takes a Solana address or token address and returns the first and last 3 characters.

    Args:
    address (str): The Solana address or token address.

    Returns:
    str: A string containing the first 3 and last 3 characters of the address, 
         separated by '...'.
    """
    if not address or len(address) < 6:
        return address  # Return the original address if it's too short

    return f"{address[:3]}...{address[-3:]}"

if __name__ == "__main__":
    #print(type(None))
    print(shorten_address("7FhLDYhLagEYx8mvheyWMo25ChQcM9F54TiM15Ydpump"))
    draw_trials("https://wsrv.nl/?w=128&h=128&default=1&url=https%3A%2F%2Fipfs.io%2Fipfs%2FQmes6UqktVkh2j8nSyDiW8nLns7Kg1UTmhy7tMnz3D9ukb", "spider cat", "scat")