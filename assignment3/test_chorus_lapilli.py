#!/usr/bin/env python3
'''Simple test harness for Chorus Lapilli.

Extend the TestChorusLapilli class to add your own tests.
'''
import os
import sys
import argparse
import subprocess
import unittest
import urllib.request
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

class TestChorusLapilli(unittest.TestCase):
    '''Integration testing for Chorus Lapilli

    This class handles the entire React startup, testing, and teardown
    process. Feel free to modify it to suit your needs.
    '''

    # ========================== [USEFUL CONSTANTS] ===========================

    # React default startup address
    REACT_HOST_ADDR = 'http://localhost:3000'

    # CSS selector used to find Chorus Lapilli board tiles
    BOARD_TILE_SELECTOR = '.square'

    # Sets of symbol classes - each string contains all valid characters
    # for that particular symbol
    SYMBOL_BLANK = ''
    SYMBOL_X = 'X'
    SYMBOL_O = 'O'

    # ======================== [SETUP/TEARDOWN HOOKS] =========================

    @classmethod
    def setUpClass(cls):
        '''This function runs before testing occurs.

        Bring up the web app and configure Selenium
        '''

        # Configure the Selenium webdriver
        try:
            cls.driver = webdriver.Chrome()  # Ensure chromedriver is in PATH
            cls.driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to appear
        except WebDriverException as e:
            print("Error initializing WebDriver.")
            print("Ensure you have the appropriate WebDriver installed and it's in your PATH.")
            raise e

        # Navigate to the Chorus Lapilli app
        cls.driver.get(cls.REACT_HOST_ADDR)

    @classmethod
    def tearDownClass(cls):
        '''This function runs after all testing have run.

        Terminate the Selenium webdriver.
        '''
        cls.driver.quit()

    def setUp(self):
        '''This function runs before every test.

        Refresh the browser so we get a new board.
        '''
        self.driver.refresh()
        time.sleep(1)  # Wait for the page to load

    def tearDown(self):
        '''This function runs after every test.

        Not needed, but feel free to add stuff here.
        '''
        pass

    # ========================== [HELPER FUNCTIONS] ===========================

    def get_tiles(self):
        '''Retrieve all board tiles as WebElements.

        Returns:
            List[WebElement]: List of 9 tile elements.
        '''
        return self.driver.find_elements(By.CSS_SELECTOR, self.BOARD_TILE_SELECTOR)

    def assertBoardEmpty(self, tiles):
        '''Checks if all board tiles are empty.

        Arguments:
            tiles: List[WebElement] - a board consisting of 9 button elements
        Raises:
            AssertionError - if board is not empty
        '''
        if len(tiles) != 9:
            raise AssertionError('tiles is not a 3x3 grid')
        for i, tile in enumerate(tiles):
            if tile.text.strip():
                raise AssertionError(f'tile {i} is not empty: '
                                     f'\'{tile.text}\'')

    def assertTileIs(self, tile, expected_symbol):
        '''Checks if a tile contains the expected symbol.

        Arguments:
            tile: WebElement - the button element to check
            expected_symbol: str - the expected symbol ('X', 'O', or '')
        Raises:
            AssertionError - if tile does not contain the expected symbol
        '''
        actual_symbol = tile.text.strip()
        self.assertEqual(actual_symbol, expected_symbol,
                         f'Expected tile to be \'{expected_symbol}\', but found \'{actual_symbol}\'')

    def get_status_text(self):
        '''Retrieve the status text displayed by the game.

        Returns:
            str: The status message.
        '''
        status_element = self.driver.find_element(By.CLASS_NAME, 'status')
        return status_element.text.strip()

    # =========================== [ADD YOUR TESTS HERE] ===========================

    def test_empty_board_on_refresh(self):
        '''Test that the board is empty upon refreshing the page.'''
        tiles = self.get_tiles()
        self.assertBoardEmpty(tiles)

    def test_first_move_places_x(self):
        '''Test that clicking the top-left tile places an 'X' on an empty board.'''
        tiles = self.get_tiles()
        tiles[0].click()
        time.sleep(0.5)  # Wait for the click action to be processed
        self.assertTileIs(tiles[0], self.SYMBOL_X)

    def test_alternate_turns(self):
        '''Check that players alternate turns and the correct symbol is placed.'''
        tiles = self.get_tiles()
        # First move by X
        tiles[0].click()
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        # Second move by O
        tiles[1].click()
        self.assertTileIs(tiles[1], self.SYMBOL_O)
        # Third move by X
        tiles[2].click()
        self.assertTileIs(tiles[2], self.SYMBOL_X)
        # Fourth move by O
        tiles[3].click()
        self.assertTileIs(tiles[3], self.SYMBOL_O)
        # Fifth move by X
        tiles[4].click()
        self.assertTileIs(tiles[4], self.SYMBOL_X)
        # Sixth move by O
        tiles[5].click()
        self.assertTileIs(tiles[5], self.SYMBOL_O)

    def test_no_moves_after_win(self):
        '''Check that after a player wins, no further moves are allowed.'''
        tiles = self.get_tiles()
        # Simulate moves leading to a win for X
        # Placement Phase
        tiles[0].click()  # X
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        tiles[3].click()  # O
        self.assertTileIs(tiles[3], self.SYMBOL_O)
        tiles[1].click()  # X
        self.assertTileIs(tiles[1], self.SYMBOL_X)
        tiles[4].click()  # O
        self.assertTileIs(tiles[4], self.SYMBOL_O)
        tiles[2].click()  # X - X should win here
        self.assertTileIs(tiles[2], self.SYMBOL_X)

        # Verify winner status
        status = self.get_status_text()
        self.assertIn('Winner: X', status, "Winner status not correctly displayed for X.")

        # Attempt to make an additional move by O
        tiles[5].click()  # O tries to move
        # Since the game is over, the tile should remain empty
        self.assertTileIs(tiles[5], self.SYMBOL_BLANK)

    def test_move_to_non_adjacent_square(self):
        '''Check that moving a piece to a non-adjacent square is not allowed.'''
        tiles = self.get_tiles()
        # Placement Phase
        tiles[0].click()  # X
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        tiles[3].click()  # O
        self.assertTileIs(tiles[3], self.SYMBOL_O)
        tiles[1].click()  # X
        self.assertTileIs(tiles[1], self.SYMBOL_X)
        tiles[4].click()  # O
        self.assertTileIs(tiles[4], self.SYMBOL_O)
        tiles[2].click()  # X
        self.assertTileIs(tiles[2], self.SYMBOL_X)
        tiles[5].click()  # O
        self.assertTileIs(tiles[5], self.SYMBOL_O)

        # Movement Phase starts
        # X needs to move since both players have placed three pieces
        # Attempt to move X from 0 to 8 (non-adjacent)
        tiles[0].click()  # Select piece at 0
        tiles[8].click()  # Try to move to 8 (should not be allowed)

        # Verify that the move did not occur
        self.assertTileIs(tiles[8], self.SYMBOL_BLANK)
        self.assertTileIs(tiles[0], self.SYMBOL_X)

    def test_vacate_center_square_rule(self):
        '''Check that a player with a piece in the center must vacate it or win.'''
        tiles = self.get_tiles()
        # Placement Phase
        tiles[0].click()  # X
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        tiles[4].click()  # O (center)
        self.assertTileIs(tiles[4], self.SYMBOL_O)
        tiles[1].click()  # X
        self.assertTileIs(tiles[1], self.SYMBOL_X)
        tiles[3].click()  # O
        self.assertTileIs(tiles[3], self.SYMBOL_O)
        tiles[2].click()  # X
        self.assertTileIs(tiles[2], self.SYMBOL_X)
        tiles[5].click()  # O
        self.assertTileIs(tiles[5], self.SYMBOL_O)

        # Movement Phase starts
        # O has a piece in the center and must either win or vacate it
        # Attempt to move a non-center piece (should not be allowed)
        tiles[3].click()  # Select piece at 3 (non-center)
        tiles[6].click()  # Try to move to 6
        # Should not be allowed; tile[6] should remain empty
        self.assertTileIs(tiles[6], self.SYMBOL_BLANK)
        # The selected piece should remain at position 3
        self.assertTileIs(tiles[3], self.SYMBOL_O)

        # O must move the center piece
        tiles[4].click()  # Select center piece
        tiles[7].click()  # Move to 7
        self.assertTileIs(tiles[4], self.SYMBOL_BLANK)
        self.assertTileIs(tiles[7], self.SYMBOL_O)

    # ================= [DO NOT MAKE ANY CHANGES BELOW THIS LINE] =================

if __name__ != '__main__':
    from selenium.webdriver import Firefox as Browser
    from selenium.webdriver.common.by import By
else:
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='Chorus Lapilli Tester')
    parser.add_argument('-b',
                        '--browser',
                        action='store',
                        metavar='name',
                        choices=['firefox', 'chrome', 'safari'],
                        default='firefox',
                        help='the browser to run tests with')
    parser.add_argument('-c',
                        '--change-dir',
                        action='store',
                        metavar='dir',
                        default=None,
                        help=('change the working directory before running '
                              'tests'))

    # Change the working directory
    options = parser.parse_args(sys.argv[1:])
    # Import different browser drivers based on user selection
    try:
        if options.browser == 'firefox':
            from selenium.webdriver import Firefox as Browser
        elif options.browser == 'chrome':
            from selenium.webdriver import Chrome as Browser
        else:
            from selenium.webdriver import Safari as Browser
        from selenium.webdriver.common.by import By
    except ImportError as err:
        print('[Error]',
              err, '\n\n'
              'Please refer to the Selenium documentation on installing the '
              'webdriver:\n'
              'https://www.selenium.dev/documentation/webdriver/'
              'getting_started/',
              file=sys.stderr)
        sys.exit(1)

    if options.change_dir:
        try:
            os.chdir(options.change_dir)
        except OSError as err:
            print(err, file=sys.stderr)
            sys.exit(1)

    if not os.path.isfile('package.json'):
        print('Invalid directory: cannot find \'package.json\'',
              file=sys.stderr)
        sys.exit(1)

    tests = unittest.defaultTestLoader.loadTestsFromTestCase(TestChorusLapilli)
    unittest.TextTestRunner().run(tests)
